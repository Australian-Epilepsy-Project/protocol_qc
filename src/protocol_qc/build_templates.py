# protocol_qc: An MRI DICOM protocol quality control tool
# Copyright (C) 2025 The Florey Institute of Neuroscience and Mental Health

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Build protocol templates from a user defined template file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path
    import logging

from protocol_qc.classes.acquisition import TemplateAcquisition
from protocol_qc.classes.protocol import TemplateProtocol
from protocol_qc.classes.series import TemplateSeries


def duplicates_settings(acq_specifications: dict[str, Any]) -> tuple[bool, int]:
    """
    Set the duplications settings for a given acquisition. If neither,
    'duplicates_expected' and 'duplicates_allowed' are set, they will
    default to 0 and False, respectively.

    Parameters
    ----------
    acq_specifications
        User defined specifications for a given acquisition.

    Returns
    -------
        (Are duplicates allowed, Number of expected duplicates)

    Raises
    ------
    ValueError
        If contradictory settings for duplicate acquisitions have been set.
    """

    # Read in template settings
    template_dupes_exp: int | None = acq_specifications.get("duplicates_expected", None)
    template_dupes_allow: bool | None = acq_specifications.get(
        "duplicates_allowed", None
    )

    # Throw error if settings are contradictory
    if template_dupes_exp is not None and template_dupes_allow is False:
        raise ValueError(
            "Contradictory acquisition settings. 'duplicates_expected' set to "
            "{template_dupes_exp} with 'duplicates_allowed' set to False."
        )

    # Set expected and allowed acquisition settings
    dupes_exp: int
    dupes_allowed: bool
    if template_dupes_allow is None:
        if (
            isinstance(template_dupes_exp, int) and template_dupes_exp == 0
        ) or template_dupes_exp is None:
            dupes_allowed = False
            dupes_exp = 0
        else:
            dupes_allowed = True
            dupes_exp = template_dupes_exp
    elif template_dupes_allow is False:
        dupes_allowed = False
        dupes_exp = 0
    elif template_dupes_allow is True:
        if (
            isinstance(template_dupes_exp, int) and template_dupes_exp == 0
        ) or template_dupes_exp is None:
            dupes_allowed = True
            dupes_exp = 0
        else:
            dupes_allowed = True
            dupes_exp = template_dupes_exp

    return dupes_allowed, dupes_exp


def set_fields(
    protocol_specifications: dict[str, Any],
    acq_specifications: dict[str, Any],
    series_specifications: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract the relevant fields for a given series template, accounting for
    the 'share_fields' flag. If the share_fields flag is set at the series
    level it will override the flag if set at the acquisition level.

    Parameters
    ----------
    protocol_specifications
        User defined specifications for a given protocol.
    acq_specifications
        User defined specifications for a given acquisition.
    series_specifications
        User defined specifications for a given series.

    Returns
    -------
        Dictionary of DICOM header fields for series template.
    """

    fields_series: dict[str, Any] = series_specifications

    share_series: bool | None = series_specifications.get("share_fields")
    share_acq: bool | None = acq_specifications.get("share_fields")

    # Share fields if 'share_field' set to True at series level,
    # or if unset and not set to False at acquisition level.
    if share_series is True or (share_series is None and share_acq is not False):
        fields_series["fields"] = {
            **protocol_specifications.get("fields", {}),
            **acq_specifications.get("fields", {}),
            **series_specifications.get("fields", {}),
        }

    return fields_series


def get_num_files(fields_series: dict[str, Any]) -> tuple[int, ...] | int | None:
    """
    Get number of expected files for series template. If neither a single value,
    or a lower and upper bound, are provided, no restriction will be set.

    Parameters
    ----------
    fields_series
        Series template.

    Returns
    -------
        Number of expected files. None if not set.

    Raises
    ------
    ValueError
        If number of files is incorrectly specified.
    """

    exp_num_files: dict[str, int] | int | None = fields_series.pop("num_files", None)

    num_files: tuple[int, ...] | int | None
    if not exp_num_files:
        assert exp_num_files is None
        num_files = exp_num_files
    elif isinstance(exp_num_files, int):
        num_files = exp_num_files
    elif isinstance(exp_num_files, dict):
        num_files = tuple([exp_num_files["min"], exp_num_files["max"]])
    else:
        raise ValueError(
            "Expected number of files must be specified as either an int or "
            "a dict containing 'min' and 'max' keys. Please check template."
        )

    return num_files


def build_templates(
    template: tuple[str, dict[str, Any]],
    min_match_score: float,
    patient_id: str,
    logger: logging.Logger,
) -> TemplateProtocol:
    """
    Build a protocol templates from the user defined template file.

    Parameters
    ----------
    template
        Path to to user defined protocol template.
    logger:
        Custom template logger.

    Returns
    -------
        Instance of TemplateProtocol.
    """

    logger.info(f"Building templates from {template[0]}...")

    template_protocol: TemplateProtocol = TemplateProtocol(template[0], logger)
    template_protocol.patient_id = patient_id

    specs_protocol: dict[str, Any] = template[1].get("GENERAL", {})

    template_protocol.set_general_settings(template[1])

    # Loop over acquisitions building individual series into classes
    for label_acq, specs_acq in template[1].items():
        logger.info(f"- Acquisition: {label_acq}")

        templates_series: list[TemplateSeries] = []
        for label_series, specs_series in specs_acq["series"].items():
            logger.info(f"   - series: {label_series}")

            fields_series: dict[str, Any] = set_fields(
                specs_protocol, specs_acq, specs_series
            )

            template_series: TemplateSeries = TemplateSeries(
                label_acq + ":" + label_series,
                logger,
                get_num_files(fields_series),
                min_match_score,
                fields=fields_series["fields"],
            )

            templates_series.append(template_series)

        dupes_allowed, dupes_expected = duplicates_settings(specs_acq)
        logger.info(f"  - duplicates allowed    = {dupes_allowed}")
        logger.info(f"  - duplicates expected   = {dupes_expected}")
        logger.info(f"  - optional acquisition  = {specs_acq.get('is_optional')}")
        logger.info(f"  - ignore ordering       = {specs_acq.get('ignore_ordering')}")

        template_protocol.template_acqs.append(
            TemplateAcquisition(
                label_acq,
                logger,
                dupes_allowed,
                dupes_expected,
                specs_acq.get("is_optional", False),
                specs_acq.get("ignore_ordering", False),
                specs_acq.get("paired_fmaps", None),
                templates_series,
            )
        )

        if specs_acq.get("paired_fmaps", None) is not None:
            template_protocol.paired_fmaps["has_paired"] = True

    return template_protocol
