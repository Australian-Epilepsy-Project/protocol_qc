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
Template protocol class.
"""

from __future__ import annotations

import dataclasses
import datetime
import logging
from typing import Any

from protocol_qc.match_statuses import MatchStatus
from protocol_qc.utils.formatting import WIDTH_TOTAL, WIDTHS

from .acquisition import TemplateAcquisition
from .dataseries import DataSeries
from .series import SeriesMatch, TemplateSeries


@dataclasses.dataclass()
class TemplateProtocol:
    """
    Template protocol.

    Parameters
    ----------
    name
        Name of the protocol template.
    logger
        Custom template logger.
    template_acqs
        List of acquisition templates that comprise the protocol.
    date_restriction
        Date restrictions set for the template.
    check_ordering
        Should the ordering of the acquisitions be checked.
    score
        Protocol matching score (fraction of acquisitions matched).
    ordering_correct
        If checked, were the acquisitions acquired in the correct order.
    paired_fmaps:
        Dictionary to store paired fmaps information.
    incomplete_data
        Do any of the matched series have missing data?
    missing_series
        Is the protocol missing any series matches?
    allow_extras
        Does the protocol template allow for extra series?
    extra_series
        The number of extra series found.
    duplicates_allowed
        Are there acquisition templates with allowed duplicate matches?
    duplicates_unexpected
        Are there acquisition templates with unexpected duplicate matches?
    duplicates_expected
        Are there acquisition templates with expected duplicate matches?
    has_issue
        Does the protocol template have any matching issues?
    optional_scans
        Were any optional acquisition templates matched?
        0: none were specified
        1: one or more specified and none found
        2: one or more specified and one or more found
    """

    name: str
    logger: logging.Logger
    template_acqs: list[TemplateAcquisition] = dataclasses.field(default_factory=list)
    date_restriction: list[datetime.date | None] = dataclasses.field(
        default_factory=list
    )
    tags: dict[str, Any] | None = None
    check_ordering: bool = False
    score: float = 0
    ordering_correct: str = "unchecked"
    paired_fmaps: dict[str, Any] = dataclasses.field(default_factory=dict)
    incomplete_data: bool = False
    missing_series: bool = False
    allow_extras: bool = False
    extra_series: int = 0
    duplicates_allowed: bool = False
    duplicates_unexpected: bool = False
    duplicates_expected: bool = False
    has_issue: bool = False
    optional_scans: int = 0
    patient_id: str | None = None

    def not_empty(self) -> bool:
        """
        Ensure protocol has defined acquisition templates.

        Returns
        -------
            Template protocol has acquisition templates?
        """

        return bool(self.template_acqs)

    def scan_dates_in_range(self, all_series: list[DataSeries]) -> bool:
        """
        Check the study date is within the specified date restriction ranges

        Returns
        -------
            SeriesDates are within allowed ranges?
        """

        if self.date_restriction[0] is None and self.date_restriction[1] is None:
            return True

        dates_list: list[datetime.date] = []
        for series in all_series:
            try:
                dates_list.append(
                    datetime.datetime.strptime(
                        str(series.data.SeriesDate), "%Y%m%d"
                    ).date()
                )
            except KeyError:
                self.logger.warning(
                    f"{series.unique_label()} does not have a s SeriesDate"
                )

        dates_unique = set(dates_list)
        self.logger.info(f"{len(dates_unique)} unique SeriesDates found in study")
        self.logger.info("Checking if date(s) of scans are within specified range...")

        # Check each scan was within the specified date ranges
        for date in dates_unique:
            if (
                self.date_restriction[0] is not None
                and self.date_restriction[1] is not None
            ):
                if not self.date_restriction[0] < date < self.date_restriction[1]:
                    self.logger.warning(
                        f"Scan performed on {date} is not within specified range."
                    )
                    return False
            if self.date_restriction[0] is None and date > self.date_restriction[1]:  # type: ignore
                self.logger.warning(
                    f"Scan performed on {date} is not within specified range."
                )
                return False
            if self.date_restriction[1] is None and date < self.date_restriction[0]:  # type: ignore
                self.logger.warning(
                    f"Scan performed on {date} is not within specified range."
                )
                return False

        return True

    def get_template_acquisitions(self) -> list[TemplateAcquisition]:
        """
        Return an exhaustive list of acquisition templates defined in the
        protocol template.

        Returns
        -------
            List of TemplateAcquisitions defined in the protocol template.
        """

        list_to_return: list[TemplateAcquisition] = []
        for template_acquisition in self.template_acqs:
            list_to_return.append(template_acquisition)

        return list_to_return

    def get_template_series(self) -> list[TemplateSeries]:
        """
        Return an exhaustive list of series template defined in the template
        protocol.

        Returns
        -------
            List of TemplateSeries defined in the protocol template.
        """

        list_to_return: list[TemplateSeries] = []
        for template_acquisition in self.template_acqs:
            for template_series in template_acquisition.template_series:
                list_to_return.append(template_series)

        return list_to_return

    def set_general_settings(self, template: dict[str, Any]) -> None:
        """
        Set all general settings for protocol template.

        Parameters
        ----------
        template
            Dict defining a protocol template.
        """

        template_general: dict[str, Any] = template.pop("GENERAL", {})

        # Set date restriction
        self._set_date_restrictions(template_general)
        # Set allow extras flag
        self._set_allow_extra(template_general)
        self._extract_tag_settings(template_general)
        self.check_ordering = template_general.get("check_ordering", False)
        self._set_paired_fmap_defaults()

    def _set_paired_fmap_defaults(self) -> None:
        """
        Set the paired fmap defaults for the template procotol.
        """

        self.paired_fmaps = {
            "has_paired": False,
            "checked": False,
            "correctly_paired": True,
        }

    def _set_allow_extra(self, template_general: dict[str, Any]) -> None:
        """
        Should an error be raised if an extra unidentified series is found?

        Parameters
        ----------
        template_general
            Template for "GENERAL" settings in a template_general protocol.
        """

        self.allow_extras = template_general.get("allow_extras", False)

        self.logger.info(
            f"Raise error if unmatched series are found: {not self.allow_extras}"
        )

    def _set_date_restrictions(
        self,
        template_general: dict[str, Any],
    ) -> None:
        """
        Set range of dates in which the template is applicable. If no range was
        specified, the value of the bound is set to None.

        Parameters
        ----------
        template_general
            Template for "GENERAL" settings in a protocol template.
        """

        # Attempt to find the date_restriction dictionary in the template
        # If none is found, return and empty dictionary
        date_restrictions: dict[Any, Any] = template_general.get("date_restriction", {})

        if date_start := date_restrictions.get("start", None):
            date_start = datetime.datetime.strptime(date_start, "%Y-%m-%d").date()
        if date_end := date_restrictions.get("end", None):
            date_end = datetime.datetime.strptime(date_end, "%Y-%m-%d").date()

        self.date_restriction.append(date_start)
        self.date_restriction.append(date_end)

        self.logger.info("The following date restrictions were extracted:")
        self.logger.info(f"  start: {self.date_restriction[0]}")
        self.logger.info(f"  end  : {self.date_restriction[1]}")

    def _extract_tag_settings(self, template_general: dict[str, Any]) -> None:
        """
        If provided, axtract the settings dictating the final version, site and
        scanner tags.

        Parameters
        ----------
        template_general
            Template for "GENERAL" settings in a protocol template.
        """

        self.tags = template_general.get("tags", None)
        if self.tags:
            self.logger.info("Tags specifications found in template.")
        else:
            self.logger.info("No tags specifications found in template.")

    def check_protocol_ordering(self) -> None:
        """
        Check if the order of acquisitions matches the order of the template, if the
        'check_ordering' flag was set in the template. If the template score was not
        1.0 or unexpected duplicates were found, this check will not be performed.
        To check the ordering, the lowest series number from each set of series making
        up and acquisition is found and then these are checked to be in increasing order.
        Within acquisition series ordering is not checked.
        """

        if not self.check_ordering:
            self.ordering_correct = "unchecked"
            self.logger.info("Acquisition ordering correct: not checked")
            return

        # Construct list of TemplateAcquisitions that should be included in ordering check,
        # and find lowest series number from series matches.
        ordered_acq_templates: list[tuple[TemplateAcquisition, int]] = []
        for acq in self.get_template_acquisitions():
            if not acq.ignore_ordering and acq.match_status == MatchStatus.MATCH:
                lowest_series_num: int = 1000000

                for series in acq.template_series:
                    try:
                        matched: SeriesMatch = [
                            x for x in series.matches if x.score == 1.0
                        ][0]
                        lowest_series_num = min(
                            lowest_series_num, matched.series_number
                        )
                    except IndexError:
                        pass

                ordered_acq_templates.append((acq, lowest_series_num))

        # Ensure the data series numbers paired to the acquisitions are in
        # increasing order
        previous_acq_num: int = -99
        for acq, num in ordered_acq_templates:
            if num < previous_acq_num:
                self.ordering_correct = "no"
                break
            previous_acq_num = num

        if self.ordering_correct == "no":
            self.logger.error("Acquisition ordering not adhered to")
            self.logger.error("AcquisitionTemplate : matched acquisition number")
            for acq, num in ordered_acq_templates:
                self.logger.error(f"{acq.name}: {num}")
            return

        self.logger.info("Acquisition ordering correct: yes")
        self.ordering_correct = "yes"

    def check_paired_fmaps(self) -> None:
        """
        Check the protocol for any fmaps that should be paired with another acquisition.
        This check will not be performed if there are any issues found with the protocol match.

        If all checks do not pass, protocol.paired_fmaps['correctly_paired'] is set to False.
        """

        if self.paired_fmaps["has_paired"] is False:
            self.logger.info("No check for paired fmaps requested.")
            return

        if self.score != 1.0 or self.duplicates_unexpected:
            self.logger.info(
                "No check for paired fmaps performed. Issue with protocol match."
            )
            return

        self.logger.info("Checking for paired fmaps...")

        # Loop over acquisitions and extract
        #  - acquisition expecting paired fmaps
        #  - fmaps
        expects_fmaps: list[TemplateAcquisition] = []
        fmaps: list[TemplateAcquisition] = []
        for acquisition in self.get_template_acquisitions():
            # Use bool() in case "paired_fmaps" has empty dictionary set for
            # an acquisition
            if bool(acquisition.paired_fmaps):
                expects_fmaps.append(acquisition)
            elif "fmaps" in acquisition.name.lower():
                fmaps.append(acquisition)

        # Now loop over acquisitions expecting fmaps
        for acquisition in expects_fmaps:
            self.logger.info(f"Checking fmaps for: {acquisition.name}")
            # Get series numbers for acquisitions
            series_nums_acqs: list[int] = []
            for series in acquisition.template_series:
                series_nums_acqs.append(
                    int([x for x in series.matches if x.score == 1.0][0].series_number)
                )
            assert acquisition.paired_fmaps is not None
            expected_pos_fmaps: str = acquisition.paired_fmaps["position"]

            # Loop over fmaps using "which_acquisitions" to create new lists of fmaps
            # to check
            fmap_series_lists: list[tuple[int, list[int]]] = []
            for expected_fmap in acquisition.paired_fmaps["which_acquisitions"]:
                # Get series numbers for fmaps
                series_nums_fmaps: list[int] = []
                num_fmap_series: int = -99
                for fmap in fmaps:
                    if expected_fmap == fmap.name:
                        num_fmap_series = len(fmap.template_series)
                        for series in fmap.template_series:
                            for data_series in (
                                x for x in series.matches if x.score == 1
                            ):
                                series_nums_fmaps.append(int(data_series.series_number))
                fmap_series_lists.append((num_fmap_series, series_nums_fmaps))

            # Loop over fmaps and determine if they are in the correct position
            first_series_acq: int = min(series_nums_acqs)
            last_series_acq: int = max(series_nums_acqs)
            for counter, fmap_series in enumerate(fmap_series_lists):
                has_match: bool = False
                if expected_pos_fmaps == "before":
                    if (
                        first_series_acq - 1 - (counter * fmap_series[0])
                        in fmap_series[1]
                    ):
                        has_match = True
                        break
                elif expected_pos_fmaps == "after":
                    if (
                        last_series_acq + 1 + (counter * fmap_series[0])
                        in fmap_series[1]
                    ):
                        has_match = True
                        break
                elif expected_pos_fmaps == "both":
                    if (
                        first_series_acq - 1 - (counter * fmap_series[0])
                        in fmap_series[1]
                        or last_series_acq + 1 + (counter * fmap_series[0])
                        in fmap_series[1]
                    ):
                        has_match = True
                        break

            if not has_match:
                self.paired_fmaps["correctly_paired"] = False
                self.logger.error(f"{acquisition.name} missing paired fmap")

            self.paired_fmaps["checked"] = True

        if self.paired_fmaps["correctly_paired"] is True:
            self.logger.info("All required paired fmaps were found")

    def print_extra_series(self, all_series: list[DataSeries]) -> None:
        """
        Determine if there are any unmatched series, set the protocol template
        unmatched attribute and print list of unmatched.

        Parameters
        ----------
        all_series
            List of DataSeries classes built from unique DICOM series.
        """

        # Create list of all data series in each templates match list
        matched_series: list[str] = []
        for template_series in self.get_template_series():
            for series in template_series.matches:
                matched_series.append(series.unique_label)

        # Reduce to only unique entries
        all_series_names: set[str] = {x.unique_label() for x in all_series}

        # Find series without a match
        unmatched: list[str] = sorted(all_series_names.difference(set(matched_series)))

        self.extra_series = len(unmatched)

        if self.extra_series > 0:
            self.logger.info("-" * WIDTH_TOTAL)
            self.logger.warning(f"{'UNMATCHED SERIES':^{WIDTH_TOTAL}}")
            self.logger.info("-" * WIDTH_TOTAL)
            for unmatch in unmatched:
                self.logger.warning(unmatch)

    def compare_series(
        self,
        all_series: list[DataSeries],
    ) -> None:
        """
        Compare the scan data against the user provided templates.
        After cross checking templates against all the DICOM series, the
        templates have their match status calculated and the results logged.

        Parameters
        ----------
        all_series
            List of DataSeries classes built from unique DICOM series.
        """

        self.logger.info("-" * WIDTH_TOTAL)
        self.logger.info("Comparing series in protocol template against data...")
        self.logger.info("-" * WIDTH_TOTAL)

        for template_series in self.get_template_series():
            self.logger.info(f" Comparing series template: {template_series.name}")
            for series in all_series:
                if not template_series.similar_series_names(series.data):
                    continue
                self.logger.info(f" -> to data series {series.unique_label()}...")
                template_series.compare_with_data_series(series)

        self.logger.info("-" * WIDTH_TOTAL)
        self.logger.info(f"{'Summary of series matches': ^{WIDTH_TOTAL}}")
        self.logger.info("-" * WIDTH_TOTAL)
        self.logger.info(
            f"{'Template':{WIDTHS[0]}} | {'MatchStatus':{WIDTHS[1]}} | "
            f"{'DataSeries':{WIDTHS[2]}} | {'Score':{WIDTHS[3]}} | {'Complete':{WIDTHS[4]}}"
        )
        self.logger.info("-" * WIDTH_TOTAL)

        for template_series in self.get_template_series():
            template_series.calc_match_status()
            template_series.print_match_status()

        self.print_extra_series(all_series)

    def compare_acquisitions(self) -> None:
        """
        Calculate match at the acquisition level by checking the match
        status of each series template.
        """

        self.logger.info("-" * WIDTH_TOTAL)
        self.logger.info(f"{'Summary of acquisition matches': ^{WIDTH_TOTAL}}")
        self.logger.info("-" * WIDTH_TOTAL)
        self.logger.info(
            f"{'Template':{WIDTHS[0]}} | {'MatchStatus':{WIDTHS[1]*3}} | "
            f"{'Score':{WIDTHS[3]}} | {'Complete':{WIDTHS[4]}}"
        )
        self.logger.info("-" * WIDTH_TOTAL)

        for template_acquisition in self.get_template_acquisitions():
            if template_acquisition.is_optional:
                self.optional_scans = 1
            template_acquisition.calc_match_status(template_acquisition.is_optional)
            template_acquisition.print_match_status()

    def compare_protocol(self, all_series: list[DataSeries]) -> None:
        """
        Calculate match of protocol. Invokes matching at series and then acquisition
        level, before calculating match of protocol.

        Parameters
        ----------
        all_series
            List of DataSeries classes to compare against protocol template.
        """

        if not self.scan_dates_in_range(all_series):
            self.logger.warning("Protocol template will not be checked")
            return

        self.compare_series(all_series)
        self.compare_acquisitions()

        matches: int = 0
        acquisition_templates = self.get_template_acquisitions()

        total_acquisitions: int = len(acquisition_templates)

        for temp_acq in acquisition_templates:
            if temp_acq.match_status == MatchStatus.MATCH:
                matches += 1
            elif temp_acq.match_status == MatchStatus.DUPES_UNEXP:
                matches += 1
                self.duplicates_unexpected = True
            elif temp_acq.match_status == MatchStatus.DUPES_ALLOW:
                matches += 1
                self.duplicates_allowed = True
            elif temp_acq.match_status == MatchStatus.DUPES_EXP:
                matches += 1
                self.duplicates_expected = True
            elif temp_acq.match_status == MatchStatus.DUPES_PARTIAL_DUPES:
                self.duplicates_unexpected = True
                total_acquisitions -= 1
            elif temp_acq.match_status == MatchStatus.NOMATCH:
                self.missing_series = True
            elif temp_acq.match_status == MatchStatus.OPTIONAL:
                self.optional_scans = 2
                total_acquisitions -= 1
            elif temp_acq.match_status == MatchStatus.OPTIONAL_PARTIAL:
                self.optional_scans = 2
                total_acquisitions -= 1
            elif temp_acq.match_status == MatchStatus.OPTIONAL_MISSING:
                total_acquisitions -= 1
            if temp_acq.incomplete_data:
                self.incomplete_data = True

        self.score = matches / total_acquisitions

        self.logger.info("-" * WIDTH_TOTAL)
        self.check_protocol_ordering()
        self.check_paired_fmaps()
        self.logger.info("-" * WIDTH_TOTAL)

        self.logger.info("")
        self.logger.info("-" * WIDTH_TOTAL)
        self.logger.info("-" * WIDTH_TOTAL)
        self.logger.info(
            f"Protocol match score {self.score:.2f} (fraction of acquisition "
            "matches)"
        )
        self.logger.info("-" * WIDTH_TOTAL)
