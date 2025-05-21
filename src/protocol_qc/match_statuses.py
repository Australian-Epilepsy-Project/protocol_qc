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
Match statuses. Used by series, acquisition and protocol templates.
"""

import enum


class MatchStatus(enum.Enum):
    """
    Enums for status of matches.
    """

    MATCH = enum.auto()
    PARTIAL = enum.auto()
    NOMATCH = enum.auto()
    MATCH_DUPES = enum.auto()
    MATCH_PARTIAL_DUPES = enum.auto()
    DUPES_EXP = enum.auto()
    DUPES_ALLOW = enum.auto()
    DUPES_UNEXP = enum.auto()
    DUPES_PARTIAL_DUPES = enum.auto()
    PARTIAL_DUPES = enum.auto()
    OPTIONAL_DUPES_PARTIAL_DUPES = enum.auto()
    MATCH_EXTRA = enum.auto()
    OPTIONAL = enum.auto()
    OPTIONAL_MISSING = enum.auto()
    OPTIONAL_PARTIAL = enum.auto()
    OPTIONAL_MATCH_PARTIAL_DUPES = enum.auto()
    UNKNOWN = enum.auto()
