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
Series template class.
"""

import dataclasses
import json
import logging
import re
from typing import Any, NamedTuple

import pydicom

from protocol_qc.classes.dataseries import DataSeries
from protocol_qc.match_statuses import MatchStatus
from protocol_qc.utils.formatting import WIDTHS

ComparisonField = NamedTuple(
    "ComparisonField", [("name", str), ("value", Any), ("comparison", str)]
)

SeriesMatch = NamedTuple(
    "SeriesMatch",
    [
        ("unique_label", str),
        ("score", float),
        ("complete", bool),
        ("series_number", int),
    ],
)


@dataclasses.dataclass()
class TemplateSeries:
    """
    Series template class to implement comparison operators, and store
    match status attributes.

    Parameters
    ----------
    name
        Name of series template.
    logger
        Custom template logger.
    num_files
        Number of expected DICOM files.
    min_match_score
        Minimum fractional score to be consider a partial match.
    fields
        Dictionary of user defined DICOM header fields to compare to data series.
    match_status
        Match status of series template.
    series_matches
        List of all data series compared to this series template.
    matches
        List of data series that had a match score above the min_match_score.
    num_dupes
        Number of duplicates (multiple matches).
    incomplete_data
        If matched, did the DICOM series have the expected number of files?
    """

    name: str
    logger: logging.Logger
    num_files: tuple[int, ...] | int | None
    min_match_score: float
    fields: dict[str, dict[str, Any]] = dataclasses.field(default_factory=dict)
    match_status: MatchStatus = MatchStatus.UNKNOWN
    series_matches: list[SeriesMatch] = dataclasses.field(default_factory=list)
    matches: list[SeriesMatch] = dataclasses.field(default_factory=list)
    num_dupes: int = 0
    incomplete_data: bool = False

    def print_match_status(self) -> None:
        """
        Print match status of a series template.
        """

        if self.match_status == MatchStatus.MATCH:
            self.logger.info(
                f"{self.name:{WIDTHS[0]}} | {'MATCH':{WIDTHS[1]}} | "
                f"{self.matches[0].unique_label:{WIDTHS[2]}} | "
                f"{self.matches[0].score:{WIDTHS[3]}.2f} | "
                f"{self.matches[0].complete!r:<{WIDTHS[4]}}"
            )
        elif self.match_status == MatchStatus.MATCH_DUPES:
            self.logger.info(
                f"{self.name:{WIDTHS[0]}} | {'DUPLICATES':{WIDTHS[1]}} "
                f"| {'---':{WIDTHS[2]}} | {'---':{WIDTHS[3]}} | {'---':{WIDTHS[4]}}"
            )
            for scan in self.matches:
                self.logger.info(
                    f"{' ':{WIDTHS[0]}} | {' ':{WIDTHS[1]}} | "
                    f"{scan.unique_label:{WIDTHS[2]}} | {scan.score:{WIDTHS[3]}.2f} | "
                    f"{scan.complete!r:<{WIDTHS[4]}}"
                )
        elif self.match_status == MatchStatus.NOMATCH:
            self.logger.info(
                f"{self.name:{WIDTHS[0]}} | {'NO MATCH':{WIDTHS[1]}} | "
                f"{' ':{WIDTHS[2]}} | {0:{WIDTHS[3]}} |"
            )
        elif self.match_status == MatchStatus.PARTIAL:
            self.logger.info(
                f"{self.name:{WIDTHS[0]}} | {'PARTIAL':{WIDTHS[1]}} | "
                f"{self.matches[0].unique_label:{WIDTHS[2]}} | "
                f"{self.matches[0].score:{WIDTHS[3]}.2f} | "
                f"{self.matches[0].complete!r:<{WIDTHS[4]}}"
            )
        elif self.match_status == MatchStatus.PARTIAL_DUPES:
            self.logger.info(
                f"{self.name:{WIDTHS[0]}} | {'PART. DUPES':{WIDTHS[1]}} "
                f"| {'---':{WIDTHS[2]}} | {'---':{WIDTHS[3]}} | {'---':{WIDTHS[4]}}"
            )
            for scan in self.matches:
                self.logger.info(
                    f"{' ':{WIDTHS[0]}} | {' ':{WIDTHS[1]}} | "
                    f"{scan.unique_label:{WIDTHS[2]}} | {scan.score:{WIDTHS[3]}.2f} | "
                    f"{scan.complete!r:<{WIDTHS[4]}}"
                )
        else:
            self.logger.error(
                f"{self.name:{WIDTHS[0]}} | {'UNCHECKED':{WIDTHS[1]}} | "
                f"{' ':{WIDTHS[2]}} | {self.matches[0].score:{WIDTHS[3]}} | "
                f"{self.matches[0].complete!r:<{WIDTHS[4]}}"
            )

    def has_missing_files(self, matches: list[SeriesMatch]) -> bool:
        """
        Check if any matched series have missing DICOM files.

        Parameters
        ----------
        matches
            List of SeriesMatch objects to check.

        Returns
        -------
            missing files?
        """

        if any(x for x in matches if x.complete is False):
            return True

        return False

    def calc_match_status(self) -> None:
        """
        Calculate the match status of a series template and set attributes
        accordingly.
        """

        # Matches
        matches = [x for x in self.series_matches if x.score == 1]
        if matches:
            if len(matches) == 1:
                self.match_status = MatchStatus.MATCH
            elif len(matches) > 1:
                self.match_status = MatchStatus.MATCH_DUPES
                self.num_dupes = len(matches) - 1
            self.incomplete_data = self.has_missing_files(matches)
            self.matches = matches
            return

        # Partial matches
        no_matches = [
            x for x in self.series_matches if self.min_match_score < x.score < 1.0
        ]
        if no_matches:
            if len(no_matches) == 1:
                self.match_status = MatchStatus.PARTIAL
            elif len(no_matches) > 1:
                self.match_status = MatchStatus.PARTIAL_DUPES
            self.incomplete_data = self.has_missing_files(no_matches)
            self.matches = no_matches
        # No match
        else:
            self.match_status = MatchStatus.NOMATCH

    def similar_series_names(self, data: pydicom.dataset.FileDataset) -> bool:
        """
        Check if a DICOM series SeriesDescription matches the SeriesDescription
        defined in the user template for a series. re.search is used for the
        match.

        Parameters
        ----------
        data
           pydicom FileDataset containing DICOM series header information.

        Returns
        -------
            Was SeriesDescription matched?
        """

        if series_desc_info := self.fields.get("SeriesDescription", None):
            template_regex: str = series_desc_info.get("value", "")
            attribute: str | None = getattr(data, "SeriesDescription", None)
            if not attribute or re.search(template_regex, attribute):
                return True
            return False

        return True

    def format_header_field(
        self,
        attr: pydicom.dataelem.DataElement,
    ) -> list[Any] | pydicom.dataelem.DataElement:
        """
        Format the pydicom DataElement from MultiValue to list.

        Parameters
        ----------
        attr
            DataElement to be checked for formatting.

        Returns
        -------
            DataElement or list.
        """

        if isinstance(attr, pydicom.multival.MultiValue):
            return list(attr)

        return attr

    # Define main function which accepts pydicom data object and loops over entries
    # Call specific functions based on header field type and comparison level
    def compare_with_data_series(
        self,
        scan: DataSeries,
    ) -> None:
        """
        Compare a series template against a DICOM series and write the result,
        as a SeriesMatch, into the series template' series_matches list.

        Parameters
        ----------
        scan
            DataSeries object containing DICOM information to be checked.
        """

        complete_data: bool = self.is_series_complete(scan)

        frac_correct: float = self.compare_header_fields(scan.data)

        self.series_matches.append(
            SeriesMatch(
                scan.unique_label(), frac_correct, complete_data, scan.data.SeriesNumber
            )
        )

    def is_series_complete(self, scan: DataSeries) -> bool:
        """
        Check the DICOM series has the expected number of files.

        Parameters
        ----------
        scan
            DataSeries being checked.

        Returns
        -------
            Is the series complete?
        """

        num_files: tuple[int, ...] | int | None
        if num_files := getattr(self, "num_files"):
            if isinstance(num_files, tuple):
                if num_files[0] <= scan.num_files and num_files[1] >= scan.num_files:
                    return True
                self.logger.error(
                    f"   files: {scan.num_files} not between {list(num_files)}"
                )
            if num_files == scan.num_files:
                return True
            self.logger.error(f"   files: {num_files} != {scan.num_files}")
            return False

        return True

    def compare_header_fields(self, data: pydicom.dataset.FileDataset) -> float:
        """
        Compare a set of fields between a series template and a DICOM series.

        Parameters
        ----------
        data
            pydicom FileDataset object from a DICOM series.

        Returns
        -------
            Fraction of the header fields that matched the series template.
        """

        num_correct: float = 0

        is_enhanced: bool = False
        if data["SOPClassUID"].repval == "Enhanced MR Image Storage":
            is_enhanced = True

        # Loop over all fields and perform comparisons
        for field_name, details in self.fields.items():
            field: ComparisonField = ComparisonField(
                name=field_name,
                value=details["value"],
                comparison=details["comparison"],
            )

            attribute: Any = None
            if is_enhanced is False:
                if "PRIVATE" in field.name:
                    attribute = self.get_non_keyword_field(field.name, data)
                else:
                    attribute = getattr(data, field.name, None)
            else:
                try:
                    attribute = self.get_enhanced_field(field_name, data)
                except KeyError:
                    self.logger.warning(f"Field {field_name} not found.")

            if attribute is None:
                self.logger.debug(f"  - {field.name} missing from series")
                continue

            attribute = self.format_header_field(attribute)

            if field.comparison == "exact":
                num_correct += self.compare_exact(field, attribute)
            elif field.comparison == "regex":
                num_correct += self.compare_regex(field, str(attribute))
            elif field.comparison == "in_range":
                num_correct += self.compare_in_range(field, attribute)
            elif field.comparison == "in_set":
                num_correct += self.compare_in_set(field, attribute)

        num_fields: int = len(self.fields)
        if num_correct != num_fields:
            self.logger.debug(f"            {100*(num_correct/num_fields):.2f}% match")

        return num_correct / len(self.fields)

    def get_non_keyword_field(
        self, field_name: str, data: pydicom.dataset.FileDataset
    ) -> Any:
        """
        Function to retrieve values of DICOM header fields that are not simple
        keyword look-ups in classic DICOM series. This includes classic DICOM
        series produced on XA systems.
        For example, data.SeriesNumber is a simple keyword
        lookup, whereas extracting the number of slices from a MOSAIC DICOM
        series requires investigating a private tag. This function retrieves
        DICOM header field information based on a mapping between the specified
        'field_name' and a specific DICOM tag.


        Currently available non_keyword maps on Siemen's VE software platform:
            - 'NumberOfImagesInMosaic' = 0x0019,0x100a
            - 'GradientMode' = 0x0019,0x100f
            - 'Orientation' = 0x0051,0x100e
            - 'AcquisitionDuration' = 0x0051,0x100a
            - 'CoilElementsUsed' = 0x0051,0x100f
            - 'ParallelImagingAcceleration' = 0x0051,0x1101
        Currently available non_keyword maps on Siemen's XA software platform:
            - 'GradientMode' = 0x0021,0x1008
            - 'ParallelImagingAcceleration' = 0x0021,0x1009
            - 'InPlanePhaseEncDirection' = 0x0021,0x111c
            - 'CoilElementsUsed' = 0x0021,0x114f
            - 'AcquisitionDuration' = 0x0051,0x100a

        Parameters
        ----------
        field_name
            Name of private DICOM header field.
        data
            FileDataset object from a DICOM series.
        Returns
        -------
            Value of non-keyword field.
        """

        return_value: Any | None = None

        # Check software version of scanner and set private fields accordingly
        private_fields: dict[str, tuple[int, int]]
        sop_class_uid: str = data["SOPClassUID"].repval
        try:
            if (
                data["ConversionSourceAttributesSequence"][0][
                    "ReferencedSOPClassUID"
                ].repval
                == "Enhanced MR Image Storage"
            ):
                was_enhanced: bool = True
            else:
                was_enhanced = False
        except KeyError:
            was_enhanced = False

        if sop_class_uid == "Enhanced MR Image Storage" or was_enhanced:
            private_fields = {
                "GradientMode": (0x0021, 0x1008),
                "ParallelImagingAcceleration": (0x0021, 0x1009),
                "InPlanePhaseEncDirection": (0x0021, 0x111C),
                "CoilElementsUsed": (0x0021, 0x114F),
                "AcquisitionDuration": (0x0051, 0x100A),
            }
        elif sop_class_uid == "MR Image Storage":
            private_fields = {
                "NumberOfImagesInMosaic": (0x0019, 0x100A),
                "GradientMode": (0x0019, 0x100F),
                "Orientation": (0x0051, 0x100E),
                "AcquisitionDuration": (0x0051, 0x100A),
                "CoilElementsUsed": (0x0051, 0x100F),
                "ParallelImagingAcceleration": (0x0051, 0x1011),
            }
        else:
            # Log error if unknown software version
            self.logger.error(
                f"Private fields for SOPClassUID {sop_class_uid} not configured"
            )
            return return_value

        for name, tag in private_fields.items():
            if field_name == "PRIVATE-" + name:
                try:
                    return_value = data[tag[0], tag[1]].value
                except KeyError:
                    break

        return return_value

    def get_enhanced_field(
        self, field_name: str, data: pydicom.dataset.FileDataset
    ) -> Any | None:
        """
        Retrieve DICOM header fields from enhanced DICOMS.

        Parameters
        ----------
        field_name
            Name of private DICOM header field.
        data
            FileDataset object from a DICOM series.
        Returns
        -------
            Value of non-keyword field.
        """

        # List of fields that can be accessed via keyword
        if field_name in [
            "Rows",
            "Columns",
            "PulseSequenceName",
            "VolumetricProperties",
            "EchoPulseSequence",
            "SeriesDescription",
            "NumberOfFrames",
            "ImageComments",
            "ComplexImageComponent",
            "ImageType",
            "SOPClassUID",
            "ContentLabel",
        ]:
            return getattr(data, field_name, None)

        to_return: Any = None

        # Private fields at the data set level
        private_fields: dict[str, tuple[int, int]] = {
            "GradientMode": (0x0021, 0x1008),
            "ParallelImagingAcceleration": (0x0021, 0x1009),
            "InPlanePhaseEncDirection": (0x0021, 0x111C),
            "CoilElementsUsed": (0x0021, 0x114F),
        }
        if field_name in private_fields:
            for tag in private_fields.values():
                try:
                    to_return = data[tag[0], tag[1]].value
                except KeyError:
                    break
            return to_return

        # Private fields in the PerFrameFunctionGroupsSequence frames
        if field_name in [
            "ImageTypeText",
            "SliceThickness",
            "EffectiveEchoTime",
            "NumberOfAverages",
        ]:
            seq_per_frame_groups: pydicom.dataset.Dataset = data[
                "PerFrameFunctionalGroupsSequence"
            ][0]
            # ImageTypeText
            if field_name == "ImageTypeText":
                # Account for data that has been resent with modified DICOM header fields
                try:
                    to_return = seq_per_frame_groups[0x0021, 0x11FE][0][
                        0x0021, 0x1175
                    ].value
                except KeyError:
                    to_return = seq_per_frame_groups[0x0021, 0x10FE][0][
                        0x0021, 0x1075
                    ].value
            # Slice Thickness
            elif field_name == "SliceThickness":
                to_return = float(
                    seq_per_frame_groups["PixelMeasuresSequence"][0][
                        "SliceThickness"
                    ].value
                )
            # EffectiveEchoTime
            elif field_name == "EffectiveEchoTime":
                to_return = seq_per_frame_groups["MREchoSequence"][0][
                    "EffectiveEchoTime"
                ].value
            # NumberOfAverages
            elif field_name == "NumberOfAverages":
                to_return = seq_per_frame_groups["MRAveragesSequence"][0][
                    "NumberOfAverages"
                ].value

            return to_return

        # Private fields in the SharedFunctionalGroupsSequence frames
        if field_name in [
            "PercentPhaseFieldOfView",
            "RepetitionTime",
            "PixelBandwidth",
            "FlipAngle",
            "EchoTrainLength",
            "MRAcquisitionPhaseEncodingSteps",
            "MRAcquisitionFrequencyEncodingSteps",
            "InversionTimes",
        ]:
            seq_shared_per_func_group: pydicom.dataset.Dataset = data[
                "SharedFunctionalGroupsSequence"
            ][0]
            # PercentPhaseFieldOfView
            if field_name == "PercentPhaseFieldOfView":
                to_return = seq_shared_per_func_group["MRFOVGeometrySequence"][0][
                    "PercentPhaseFieldOfView"
                ].value
            # MRAcquisitionFrequencyEncodingSteps
            elif field_name == "MRAcquisitionFrequencyEncodingSteps":
                to_return = seq_shared_per_func_group["MRFOVGeometrySequence"][0][
                    "MRAcquisitionFrequencyEncodingSteps"
                ].value
            # MRAcquisitionPhaseEncodingSteps
            elif field_name == "MRAcquisitionPhaseEncodingSteps":
                to_return = seq_shared_per_func_group["MRFOVGeometrySequence"][0][
                    "MRAcquisitionPhaseEncodingStepsInPlane"
                ].value
            # RepetitionTime
            elif field_name == "RepetitionTime":
                to_return = seq_shared_per_func_group[
                    "MRTimingAndRelatedParametersSequence"
                ][0]["RepetitionTime"].value
            # PixelBandWidth
            elif field_name == "PixelBandwidth":
                to_return = seq_shared_per_func_group["MRImagingModifierSequence"][0][
                    "PixelBandwidth"
                ].value
            # FlipAngle
            elif field_name == "FlipAngle":
                to_return = seq_shared_per_func_group[
                    "MRTimingAndRelatedParametersSequence"
                ][0]["FlipAngle"].value
            # EchoTrainLength
            elif field_name == "EchoTrainLength":
                to_return = seq_shared_per_func_group[
                    "MRTimingAndRelatedParametersSequence"
                ][0]["EchoTrainLength"].value
            # InversionTimes
            elif field_name == "InversionTimes":
                to_return = seq_shared_per_func_group["MRModifierSequence"][0][
                    "InversionTimes"
                ].value

            return to_return

        return None

    def compare_exact(self, field: ComparisonField, attribute: Any) -> int:
        """
        Determine if the header fields are an exact match.

        Parameters
        ----------
        field
            Value of the user specified field from template procotol.
        attribute
            Corresponding value of the field from a DICOM series.

        Returns
        -------
            1 if a match, 0 if not.
        """

        if field.value == attribute:
            return 1

        self.logger.debug(f"    {field.name}: {field.value} != {attribute}")
        return 0

    def compare_regex(self, field: ComparisonField, attribute: str) -> int:
        """
        Determine if the DICOM header field matches the regex specified in the
        template. If the attribute is a list (e.g., ImageType),
        the individual entries will be compared. The template list can be shorter
        than the data list, in which case only a portion of the data list will be
        checked.

        Parameters
        ----------
        field
            Value of the user specified field from template procotol.
        attribute
            Corresponding value of the field from a DICOM series.

        Returns
        -------
            1 if a match, 0 if not.
        """

        if isinstance(field.value, list):
            if isinstance(attribute, str):
                attribute = json.loads(attribute.replace("'", '"'))
            for val1, val2 in zip(field.value, attribute):
                if not re.search(val1, val2):
                    break
            else:
                return 1
        else:
            if re.search(field.value, attribute):
                return 1

        self.logger.debug(
            f"    {field.name}: {field.value} regex not matched to {attribute}"
        )
        return 0

    def compare_in_range(self, field: ComparisonField, attribute: Any) -> int:
        """
        Determine if the DICOM header field is within a certain range. The
        bounds are inclusive.

        Parameters
        ----------
        field
            Value of the user specified field from template procotol.
        attribute
            Corresponding value of the field from a DICOM series.

        Returns
        -------
            1 if a match, 0 if not.
        """

        if field.value[0] <= float(attribute) <= field.value[1]:
            return 1

        self.logger.debug(
            f"    {field.name}: {float(attribute)} not within range ({field.value})"
        )
        return 0

    def compare_in_set(self, field: ComparisonField, attribute: Any) -> int:
        """
        Determine if the DICOM header field is contained within a set of values.

        Parameters
        ----------
        field
            Value of the user specified field from template procotol.
        attribute
            Corresponding value of the field from a DICOM series.

        Returns
        -------
            1 if a match, 0 if not.
        """

        if attribute in field.value:
            return 1

        self.logger.debug(f"    {field.name}: {attribute} not in set ({field.value})")
        return 0
