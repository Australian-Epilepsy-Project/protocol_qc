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
Summarise all protocol template matches.
"""

from __future__ import annotations

import logging

from protocol_qc.classes.protocol import TemplateProtocol
from protocol_qc.utils.formatting import WIDTH_TOTAL


def print_exact_match(protocols: list[TemplateProtocol], logger: logging.Logger) -> int:
    """
    Print a summary indicating whether a unique match was found and return an
    appropriate exit code.

    Parameters
    ----------
    protocols:
        List of all checked TemplateProtocols.
    logger:
        Custom summary logger.

    Returns
    -------
        0 - if unique match
        1 - if multiple matches
        2 - if no matches
    """

    # Reduce list of protocols to only full matches with no issues
    matched: list[TemplateProtocol] = [
        x for x in protocols if x.score == 1 and not x.has_issue
    ]

    logger.info("-" * WIDTH_TOTAL)
    logger.info("-" * WIDTH_TOTAL)

    if len(matched) == 1:
        logger.info("The following template was matched:")
        logger.info(f" - {protocols[0].name}: {protocols[0].score:.2f}")
        if protocols[0].duplicates_allowed:
            logger.info("  - allowed duplicates exist for one or more acquisitions")
        exit_code = 0
    elif len(matched) > 1:
        logger.error(
            "Multiple templates were matched;"
            " see above list and individual logs for details"
        )
        exit_code = 1
    else:
        logger.error(
            "No templates were perfectly matched;"
            " see above list and individual logs for details"
        )
        exit_code = 2

    logger.info("-" * WIDTH_TOTAL)

    return exit_code


def summarise_protocol_matches(
    protocols: list[TemplateProtocol],
    min_match_score: float,
    logger: logging.Logger,
) -> int:
    """
    Summarise all the protocol matches.

    Parameters
    ----------
    protocols:
        List of all checked TemplateProtocols.
    min_match_score
        Minimum fractional match for DICOM header fields for a series to be
        seen as a potential match
    logger:
        Custom summary logger.

    Returns
    -------
        0 - if unique match
        1 - if multiple matches
        2 - if no matches
    """

    # Print protocol matches
    logger.info("-" * WIDTH_TOTAL)
    logger.info(f"{'Summarising protocol matches':^{WIDTH_TOTAL}}")
    logger.info("-" * WIDTH_TOTAL)

    # Order list of protocols
    protocols.sort(key=lambda x: x.duplicates_unexpected)
    protocols.sort(key=lambda x: x.extra_series)
    protocols.sort(key=lambda x: x.incomplete_data)
    protocols.sort(key=lambda x: x.score, reverse=True)

    # Track the number of protocol templates not listed in the summary due to
    # their match scores being below the min_match_score.
    not_shown: int = 0

    for protocol in protocols:
        score: float = protocol.score
        if score < min_match_score:
            not_shown += 1
            continue
        if protocol.incomplete_data:
            score_print: str = f"{score:.2f} (MISSING DATA)"
            protocol.has_issue = True
        else:
            score_print = f"{score:.2f}"
        logger.info(f" - {protocol.name}: {score_print}")
        # Only print out additional information if matched
        if protocol.missing_series:
            logger.info("   - one or more acquisition templates were unmatched")
            protocol.has_issue = True
        if protocol.duplicates_unexpected:
            logger.info(
                "   - wrong number of duplicates for one or more acquisition templates"
            )
            protocol.has_issue = True
        if protocol.ordering_correct == "no":
            logger.info("   - acquisitions not in expected order")
            protocol.has_issue = True
        if protocol.paired_fmaps["checked"] is True:
            if protocol.paired_fmaps["correctly_paired"] is False:
                logger.info("   - issue with one or more fmap pairings")
                protocol.has_issue = True
        if protocol.extra_series:
            if not protocol.allow_extras:
                allow: str = "unexpected"
                protocol.has_issue = True
            else:
                allow = "allowed"
            logger.info(
                f"   - {protocol.extra_series} extra series were detected ({allow})"
            )
        if protocol.duplicates_allowed:
            logger.info("   - duplicates exist for one or more acquisitions (allowed)")
        if protocol.optional_scans == 2:
            logger.info("   - one or more optional scans present")

    if not_shown:
        logger.info("-" * WIDTH_TOTAL)
        logger.info(
            f" - {not_shown} protocol template matches not shown due to match "
            f"score less than {min_match_score}"
        )

    return print_exact_match(protocols, logger)
