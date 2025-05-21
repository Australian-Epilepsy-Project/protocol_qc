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
Generate a tags file from a template protocol.
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any

from protocol_qc._version import __version__

from .classes.dataseries import DataSeries
from .classes.protocol import TemplateProtocol


def gen_custom_tags(
    protocol: TemplateProtocol,
    tags_output: dict[str, Any],
    data_series: DataSeries,
) -> None:
    """
    Generate custom tags as defined in the protocol template.

    Parameters
    ----------
    protocol
        TemplateProtocol from which tags will be generated.
    tags_output
        dict containing tags to be saved.
    data_series
        A single DataSeries classes built from a unique DICOM series.
    """

    if not protocol.tags:
        return

    tags_output["custom_tags"] = {}

    for tag_type, value in protocol.tags.items():
        if value["type"] == "constant":
            tags_output["custom_tags"][tag_type] = value["tag"]
        elif value["type"] == "fill_with":
            try:
                tags_output["custom_tags"][tag_type] = getattr(
                    data_series.data, value["tag"]
                )
            except KeyError:
                tags_output["custom_tags"][tag_type] = "NOT FOUND"
        elif isinstance(value["tag"], dict):
            for tag, to_check in value["tag"].items():
                if "PRIVATE-" in to_check["field"]:
                    raise KeyError(
                        "Cannot use private DICOM fields when generating tags"
                    )
                try:
                    if attr := getattr(data_series.data, to_check["field"]):
                        if to_check["comparison"] == "exact":
                            if attr == to_check["value"]:
                                break
                        elif to_check["comparison"] == "in_set":
                            if attr in to_check["value"]:
                                break
                        elif to_check["comparison"] == "regex":
                            if re.search(to_check["value"], attr):
                                break
                        elif to_check["comparison"] == "in_range":
                            if to_check["value"][0] <= float(attr) <= to_check["value"]:
                                break
                except AttributeError:
                    pass
            else:
                protocol.logger.warning(f"No match found for tag: {tag_type}")
                continue

            tags_output["custom_tags"][tag_type] = tag

        else:
            raise ValueError(
                "Invalid tag entry set in template for {key}.\n"
                "Key must be a string or dictionary"
            )


def gen_protocol_tags(protocol: TemplateProtocol, tags_output: dict[str, Any]) -> None:
    """
    Generate the acquisition and series level tags.

    Parameters
    ----------
    protocol
        TemplateProtocol from which tags will be generated.
    tags_output
        Dictionary containing tags to be saved.
    """

    tags_output["protocol"] = {
        "template_name": protocol.name,
        "protocol_match_score": protocol.score,
        "has_issue": protocol.has_issue,
        "correct_ordering": protocol.ordering_correct,
        "missing_data": protocol.incomplete_data,
        "duplicates_allowed": protocol.duplicates_allowed,
        "extra_series": {
            "allowed": protocol.allow_extras,
            "extra_series": protocol.extra_series,
        },
        "acquisitions": {},
    }

    # Paired fmap status
    if protocol.paired_fmaps["checked"] is False:
        tags_output["protocol"]["paired_fmaps"] = "unchecked"
    elif protocol.paired_fmaps["correctly_paired"] is False:
        tags_output["protocol"]["paired_fmaps"] = "pairing_issue"
    else:
        tags_output["protocol"]["paired_fmaps"] = "paired_correctly"

    # Status of optional scans
    if protocol.optional_scans == 0:
        tags_output["protocol"]["optional_scans"] = {
            "specified": "none",
            "found": "none",
        }
    elif protocol.optional_scans == 1:
        tags_output["protocol"]["optional_scans"] = {
            "specified": "one_or_more",
            "found": "none",
        }
    elif protocol.optional_scans == 2:
        tags_output["protocol"]["optional_scans"] = {
            "specified": "one_or_more",
            "found": "one_or_more",
        }

    # Loop over acquisition and series templates and set tags accordingly
    for acq in protocol.get_template_acquisitions():
        tags_output["protocol"]["acquisitions"][acq.name] = {
            "duplicates_allowed": acq.duplicates_allowed,
            # This is an unfortunate hack
            "duplicates_expected": (
                0 if acq.duplicates_expected == 0 else acq.duplicates_expected - 1
            ),
            "duplicates_found": acq.duplicates,
            "acquisitions": [],
        }
        for _ in range(int(acq.duplicates + 1)):
            tags_prot: dict[str, Any] = {
                "acquisition_match_score": float(acq.score),
                "series": {},
            }

            tags_output["protocol"]["acquisitions"][acq.name]["acquisitions"].append(
                tags_prot
            )
            for series in acq.template_series:

                # Gather matches. Single highest, or list of equally matched
                matched: list[str] = []
                highest_match_score: float = 0.01
                for match in series.matches:
                    if match.score > highest_match_score:
                        matched = [match.unique_label]
                        highest_match_score = match.score
                    elif match.score == highest_match_score:
                        matched.append(match.unique_label)
                        highest_match_score = match.score

                # Check if there were not matches and set values accordingly
                tags_series: dict[str, Any] = {
                    "series_match_score": highest_match_score if matched else 0.0,
                    # "matched": series.matches[i].unique_label if has_match else None,
                    "matched": matched if matched else None,
                    "data_complete": not series.incomplete_data if matched else "NA",
                }
                name_series: str = series.name.split(":")[1]
                tags_output["protocol"]["acquisitions"][acq.name]["acquisitions"][-1][
                    "series"
                ][name_series] = tags_series


def generate_tags(
    protocols: list[TemplateProtocol],
    data_series: DataSeries,
    which_tags: str,
    sub_label: str | None,
    path_tags: Path | None,
) -> None:
    """
    Generate a json file containing tags for the analysed subject.

    Parameters
    ----------
    protocols
        List of all checked TemplateProtocols.
    data_series
        A DataSeries class built from a unique DICOM series.
    which_tags
        String specifying for which protocols tags should be generated.
    sub_label
        User defined label for the subject to be stored in the tags file.
    path_tags
        Path to directory where tags file should be generated.
    """

    if which_tags == "none":
        return

    # Sort protocols by score
    protocols.sort(key=lambda x: x.score, reverse=True)

    # Set the required score needed to generate a tags file.
    # A lower limit of 0.4 is the base line.
    required_score: float = 0.0
    if which_tags == "highest":
        if not protocols[0].score > 0.4:
            return
        required_score = protocols[0].score

    # Filter those with the required score or higher
    protocols_high_score: list[TemplateProtocol] = list(
        filter(lambda x: x.score >= required_score, protocols)
    )

    # Filter out those with has_issue flag set
    protocols_no_issues: list[TemplateProtocol] = list(
        filter(lambda y: y.has_issue is False, protocols_high_score)
    )

    # If a single protocol has no issues, only generate tags for that template
    if len(list(protocols_no_issues)) == 1:
        protocols_high_score = protocols_no_issues

    for protocol in protocols_high_score:
        protocol.logger.info("Generating tags file...")

        # dict to store tags
        tags_output: dict[str, Any] = {}

        # Store software version and date
        tags_output["software"] = {
            "generated_with": "protocol_qc",
            "version": __version__,
            "date": datetime.datetime.today().strftime("%Y-%m-%d"),
        }

        # Subject related details
        tags_output["subject_details"] = {}

        if sub_label:
            tags_output["subject_details"]["custom_label"] = sub_label

        tags_output["subject_details"]["patientID"] = protocol.patient_id

        # Generate the site, scanner and version tags ("custom tags")
        gen_custom_tags(protocol, tags_output, data_series)

        # Generate the protocol, acquisition and series tags
        gen_protocol_tags(protocol, tags_output)

        # Write to file
        tags_filename: str
        if sub_label:
            tags_filename = f"sub-{sub_label}_tags_" + protocol.name
        else:
            tags_filename = f"patientID_{protocol.patient_id}_tags_" + protocol.name

        tags_file: Path
        if path_tags:
            tags_file = path_tags / tags_filename
        else:
            tags_file = Path.cwd() / tags_filename

        with tags_file.open("w", encoding="utf-8") as out_file:
            json.dump(tags_output, out_file, indent=2)

        protocol.logger.info(f"Tags file written to: {tags_file}")
