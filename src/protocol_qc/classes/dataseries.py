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
A wrapper class for DICOM data built.
"""

import dataclasses
from pathlib import Path

import pydicom


@dataclasses.dataclass()
class DataSeries:
    """
    Scan class to to wrap a pydicom.dataset.FileDataset object.

    Parameters
    ----------
    data
        pydicom.dataset.FileDataset for a single DICOM slice.
    num_files
        Number of files sharing the same SeriesUID as the single DICOM stored in
        'data'
    path:
        Path to the single DICOM slice used to compare against the use defined
        templates.
    """

    data: pydicom.dataset.FileDataset
    num_files: int
    path: Path

    def __str__(self) -> str:
        return (
            f"{self.data.SeriesNumber}:{self.data.SeriesDescription} with "
            f"{self.num_files} file(s)."
        )

    def unique_label(self) -> str:
        """Return a unique label to associate with the scan"""
        return f"{self.data.SeriesNumber}:{self.data.SeriesDescription}"
