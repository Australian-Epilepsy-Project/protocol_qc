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
Acquisition template class.
"""

import dataclasses
import logging
from typing import Any

from protocol_qc.match_statuses import MatchStatus
from protocol_qc.utils.formatting import WIDTHS

from .series import TemplateSeries


@dataclasses.dataclass(frozen=False)
class TemplateAcquisition:
    """
    Acquisition template with related match statuses of the data DICOM series
    under investigation.

    Parameters
    ----------
    name
        Name of acquisition template.
    logger
        Custom template logger.
    duplicates_allowed
        Are duplicates allowed?
    duplicates_expected
        Number of expected duplicates.
    is_optional
        Is this acquisition optional?
    ignore_ordering
        If the protocol ordering is checked, should this acquisition be included
    paired_fmaps
        Set of expected pair fmaps and there relative location. None otherwise
    template_series
        List of series template that make up this acquisition.
    matches_unique
        List of data series with only unique matches to series from this acquisition.
    matches_duplicates
        List of data series with multiple series template matches from this acquisition.
    matches_none
        List of data series with no template matches from this acquisition.
    match_status
        Match status of acquisition after comparing with data.
    duplicates
        Number of duplicate acquisition matches.
    incomplete_data
        Is this data set incomplete?
    score
        Acquisition match score. Fraction of matched acquisitions.
    """

    name: str
    logger: logging.Logger
    duplicates_allowed: bool = False
    duplicates_expected: int = 0
    is_optional: bool = False
    ignore_ordering: bool = False
    paired_fmaps: dict[str, Any] | None = None
    template_series: list[TemplateSeries] = dataclasses.field(default_factory=list)
    # These attributes will be set once the initial series matching has been performed
    matches_unique: list[TemplateSeries] = dataclasses.field(default_factory=list)
    matches_duplicates: list[TemplateSeries] = dataclasses.field(default_factory=list)
    matches_none: list[TemplateSeries] = dataclasses.field(default_factory=list)
    match_status: MatchStatus = MatchStatus.UNKNOWN
    duplicates: float = 0
    incomplete_data: bool = False
    score: float = 0

    def calc_match_status(self, is_optional: bool) -> None:
        """
        Calculate the match status of a acquisition template.
        First, the series matches into grouped into separate lists based on
        their match status. Following that, the lists are probed to determine
        the match status of the acquisition.

        Parameters
        ----------
        is_optional
            Is this scan an optional scan?
        """

        num_exp_series: int = len(self.template_series)

        # Group matched series into appropriate lists
        for series in self.template_series:
            if series.match_status == MatchStatus.MATCH:
                self.matches_unique.append(series)
            elif series.match_status == MatchStatus.MATCH_DUPES:
                self.matches_duplicates.append(series)
            elif series.match_status in [
                MatchStatus.NOMATCH,
                MatchStatus.PARTIAL,
                MatchStatus.DUPES_PARTIAL_DUPES,
            ]:
                self.matches_none.append(series)
            if series.incomplete_data is True:
                self.incomplete_data = True

        num_matches_unique = len(self.matches_unique)
        num_matches_none = len(self.matches_none)
        num_matches_dupes = len(self.matches_duplicates)

        # Assign labels to acquisition template based on above groups
        # MATCH: All series uniquely match
        if (
            num_matches_unique == num_exp_series
            and num_matches_dupes == 0
            and num_matches_none == 0
        ):
            if self.duplicates_expected == 0:
                self.duplicates = 0
                self.score = len(self.matches_unique) / num_exp_series
                if not is_optional:
                    self.match_status = MatchStatus.MATCH
                else:
                    self.match_status = MatchStatus.OPTIONAL
            else:
                self.match_status = MatchStatus.DUPES_UNEXP
                self.score = (
                    len(self.matches_unique) / num_exp_series
                ) / self.duplicates_expected
        # PARTIAL: One or more series with no match
        elif (
            0 < num_matches_none < num_exp_series
            and num_matches_unique != 0
            and num_matches_dupes == 0
        ):
            if not is_optional:
                self.match_status = MatchStatus.PARTIAL
                self.score = num_matches_unique / num_exp_series
            else:
                self.match_status = MatchStatus.OPTIONAL_PARTIAL

        # Duplicates exist
        elif num_matches_dupes > 0:

            series_dupes: list[int] = [x.num_dupes for x in self.matches_duplicates]
            has_equal_dupes: bool = len(set(series_dupes)) == 1

            # Calculate the number of complete matched acquisitions over expected
            if self.duplicates_expected > 0:
                self.score = (min(series_dupes) + 1) / float(self.duplicates_expected)
            else:
                self.score = 0

            # DUPLICATES: All series have same number of duplicates
            if (
                num_matches_dupes == num_exp_series
                and num_matches_unique == 0
                and num_matches_none == 0
                and has_equal_dupes is True
            ):

                # Get the number of duplicates
                self.duplicates = series_dupes[0]

                if self.duplicates_allowed:
                    if self.duplicates_expected > 0:
                        if self.duplicates == self.duplicates_expected - 1:
                            self.match_status = MatchStatus.DUPES_EXP
                        elif self.duplicates != self.duplicates_expected - 1:
                            self.match_status = MatchStatus.DUPES_UNEXP
                    else:
                        self.match_status = MatchStatus.DUPES_ALLOW
                else:
                    self.match_status = MatchStatus.DUPES_UNEXP
                self.score = 1
            # Differing numbers of duplicate matches between the series of an acquisition
            else:
                if not is_optional:
                    self.match_status = MatchStatus.DUPES_PARTIAL_DUPES
                else:
                    self.match_status = MatchStatus.OPTIONAL_DUPES_PARTIAL_DUPES

        # NOMATCH: Acquisitions with matching issues.
        # This is a catch all that covers:
        #    - partial matches with one or more have duplicate matches
        #    - full match but with one or more having duplicates
        else:
            if not is_optional:
                self.match_status = MatchStatus.NOMATCH
            else:
                self.match_status = MatchStatus.OPTIONAL_MISSING

    def print_match_status(self) -> None:
        """
        Print the match match status of a acquisition template.
        """

        status_string = ""
        if self.match_status == MatchStatus.MATCH:
            status_string = "MATCH"
        elif self.match_status == MatchStatus.DUPES_EXP:
            status_string = "DUPLICATES (EXPECTED)"
        elif self.match_status == MatchStatus.DUPES_ALLOW:
            status_string = "DUPLICATES (ALLOWED)"
        elif self.match_status == MatchStatus.DUPES_UNEXP:
            status_string = "DUPLICATES (UNEXPECTED)"
        elif self.match_status == MatchStatus.DUPES_PARTIAL_DUPES:
            status_string = "DUPLICATES (with PARTIAL DUPES)"
        elif self.match_status == MatchStatus.PARTIAL:
            status_string = "PARTIAL"
        elif self.match_status == MatchStatus.MATCH_PARTIAL_DUPES:
            status_string = "MATCH with PARTIAL DUPES"
        elif self.match_status == MatchStatus.OPTIONAL:
            status_string = "MATCH (OPTIONAL ACQUISITION)"
        elif self.match_status == MatchStatus.OPTIONAL_MISSING:
            status_string = "NOMATCH (OPTIONAL ACQUISITION)"
        elif self.match_status == MatchStatus.OPTIONAL_PARTIAL:
            status_string = "PARTIAL (OPTIONAL ACQUISITION)"
        elif self.match_status == MatchStatus.OPTIONAL_MATCH_PARTIAL_DUPES:
            status_string = "MATCH with PARTIAL DUPES (OPTIONAL ACQUISITION)"
        elif self.match_status == MatchStatus.NOMATCH:
            status_string = "NOMATCH"
        elif self.match_status == MatchStatus.UNKNOWN:
            status_string = "UNKNOWN (ERROR)"

        self.logger.info(
            f"{self.name:{WIDTHS[0]}} | {status_string:{WIDTHS[1]*3}} | "
            f"{self.score:<{WIDTHS[3]}.2f} | {not self.incomplete_data!r:<{WIDTHS[4]}}"
        )
