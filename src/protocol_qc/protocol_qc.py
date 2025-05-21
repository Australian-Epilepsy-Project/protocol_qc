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
Main protocol_qc function.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    import argparse

    from protocol_qc.classes.dataseries import DataSeries
    from protocol_qc.classes.protocol import TemplateProtocol

from protocol_qc import (
    build_templates,
    generate_tags,
    read_dicoms,
    read_templates,
    summary,
)
from protocol_qc.utils import cust_logging


def run(
    *,
    template_path: Path,
    acquisitions: Path,
    logs_dir: Path,
    find_first: bool,
    min_match_score: float,
    sub_label: str,
    which_tags: str,
    debug_level: int,
) -> int:  # pragma: no cover
    """
    Main function.

    Parameters
    ----------
    template_path
        Path to a template or directory containing template(s).
    acquisitions
        Path to directory containing DICOMs to be analysed.
    logs_dir
        Path to directory where logs should be saved.
    find_first
        Stop after a perfect template match is found.
    min_match_score
        Minimum fractional match for DICOM header fields for a series to be
        seen as a potential match.
    sub_label
        Custom subject label to store in the generated tags file.
    which_tags
        String specifying for which protocols tags should be generated.
    debug_level
        Logging level.

    Returns
    -------
        Exit code.
    """

    dir_logs: Path = cust_logging.set_logging_dir(logs_dir)

    logger_main: logging.Logger = cust_logging.custom_logger(
        "summary", dir_logs, debug_level
    )

    templates: list[tuple[str, dict[str, Any]]] = read_templates.get_templates(
        template_path, logger_main
    )

    # Find all unique series in provided directory
    all_series: list[DataSeries] = read_dicoms.find_unique_series(
        acquisitions, logger_main
    )

    # To store each protocol template that has been crossed checked
    protocols: list[TemplateProtocol] = []

    # Loop over all user provided templates and cross check against input DICOM series
    for template in templates:
        logger_main.info(f"Comparing data to: {template[0]}")

        logger_template: logging.Logger = cust_logging.custom_logger(
            template[0], dir_logs, debug_level
        )

        # Build acquisition and scan classes from user input
        template_protocol: TemplateProtocol = build_templates.build_templates(
            template, min_match_score, all_series[0].data.PatientID, logger_template
        )

        template_protocol.compare_protocol(all_series)

        protocols.append(template_protocol)

        if find_first and template_protocol.score == 1:
            logger_main.info("Exact match found. No further templates will be checked!")
            break

        # Clean up log if match is less than min_match_score
        if template_protocol.score < min_match_score:
            Path(logger_template.handlers[0].baseFilename).unlink()  # type: ignore

    # Print summaries and set has_issue flags
    ret_val: int = summary.summarise_protocol_matches(
        protocols, min_match_score, logger_main
    )

    # Generate the requested tags
    generate_tags.generate_tags(
        protocols, all_series[0], which_tags, sub_label, dir_logs
    )

    # If there was a 100% match, then remove any other template summaries
    # Use the generation of a tags file to determine which log to keep
    if ret_val == 0:
        tags_files: list[Path] = list(dir_logs.glob("*tags*.json"))
        if len(tags_files) == 1:
            # Grab protocol template name
            if protocol_name := re.search(r".*_tags_(.*)\.json", tags_files[0].name):
                for log_file in dir_logs.glob("*.log"):
                    if "summary.log" == log_file.name:
                        continue
                    if protocol_name.group(1) not in log_file.name:
                        log_file.unlink()

    return ret_val
