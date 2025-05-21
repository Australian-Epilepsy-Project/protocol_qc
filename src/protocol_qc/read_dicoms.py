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
Module to read in DICOMs and find all unique series.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    import logging

import pydicom

from protocol_qc.classes.dataseries import DataSeries

# Set to True to convert the value(s) of elements with a VR of DA, DT
# and TM to datetime.date, datetime.datetime and datetime.time respectively.
pydicom.config.datetime_conversion = True


def construct_classes(unique: dict[str, dict[str, Any]]) -> list[DataSeries]:
    """
    Construct the DataSeries classes from a list of unique DICOM series.
    The returned list is ordered by SeriesNumber.

    Parameters
    ----------
    unique
        Dictionary of unique data series.

    Returns
    -------
        List of unique DataSeries classes.
    """

    all_series: list[DataSeries] = []
    for series in unique.values():
        data: pydicom.dataset.FileDataset = pydicom.dcmread(series["path"])

        in_scan: DataSeries = DataSeries(data, series["files"], Path(series["path"]))
        all_series.append(in_scan)

    all_series.sort(key=lambda x: x.data.SeriesNumber)

    return all_series


def number_of_files(all_series: list[DataSeries], logger: logging.Logger) -> None:
    """
    Calculate the total number of files for the dataset being checked.

    Parameters
    ----------
    all_series
        List of all unique DataSeries classes.
    logger:
        Custom summary logger.
    """

    num_files: int = 0
    for a_series in all_series:
        logger.info(a_series)
        num_files += a_series.num_files

    logger.info(f"Total DICOM files: {num_files}")


def find_unique_series(dir_input: Path, logger: logging.Logger) -> list[DataSeries]:
    """
    Find all unique series in the input directory by searching for unique
    SeriesUID fields.

    Parameters
    ----------
    dir_input
        Path to directory containing DICOM series to be analysed.
    logger:
        Custom summary logger.

    Returns
    -------
        List of DataSeries classes built from unique DICOM series.

    Raises
    ------
    FileNotFoundError
        If directory does not exist or if DICOMS can not be located in the
        provided directory.
    """

    if not dir_input.is_dir():
        raise FileNotFoundError(f"Could not locate input directory: {dir_input}")

    logger.info(f"Finding unique series in: {dir_input}/")

    unique_series: dict[str, dict[str, Any]] = {}

    for input_file in dir_input.rglob("*"):
        if not input_file.is_file() or not pydicom.misc.is_dicom(input_file):
            continue

        dicom_data: pydicom.dataset.FileDataset = pydicom.dcmread(input_file)

        # Extract acquisition UID and series number
        series_uid: str = dicom_data.SeriesInstanceUID

        if series_uid not in unique_series:
            unique_series[series_uid] = {
                "files": 1,
                "path": input_file.as_posix(),
            }
        else:
            unique_series[series_uid]["files"] += 1

    if not unique_series:
        raise FileNotFoundError(f"Could not locate any DICOMS in: {dir_input}")

    all_series: list[DataSeries] = construct_classes(unique_series)

    number_of_files(all_series, logger)

    logger.info(f"Unique series found: {len(unique_series)}")

    return all_series
