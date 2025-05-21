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
Protocol_qc parser.
"""

import argparse
from pathlib import Path

from rich_argparse import RawDescriptionRichHelpFormatter

from protocol_qc._version import __version__


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Parameters
    ----------
    args
        Optional list of arguments to be passed. If a list is not provided,
        CLI arguments will be passed.

    Returns
    -------
        Namespace containing passed arguments.
    """

    usage_message = """example:

    protocol_qc my_protocol_template.json directory_of_dicoms/

    """

    parser = argparse.ArgumentParser(
        description="protocol_qc: a simple package to ensure an MRI "
        "protocol was adhered to by comparing DICOM data to one or more user "
        "defined templates.",
        formatter_class=RawDescriptionRichHelpFormatter,
        epilog=usage_message,
        add_help=False,
    )

    parser.add_argument(
        "template_path",
        help="A json file containing the protocol template, or a folder containing "
        "multiple protocol templates. If that later is provided, all protocol "
        "templates in the folder will be compared to the data.",
        type=Path,
    )
    parser.add_argument(
        "acquisitions",
        help="A path to the root directory containing the DICOM series which are to "
        "be compared against the protocol templates.",
        type=Path,
    )

    # Optional
    args_opt = parser.add_argument_group("optional")
    args_opt.add_argument(
        "--min_match_score",
        help="Fractional match score used to consider matches for series and protocols. "
        "At the series level, anything match score below this value will not be "
        "considered (even for a partial match). At the protocol level, matches below "
        "this value will not be included in the summary of protocol matches. (default: 0.8)",
        type=float,
        default=0.8,
    )
    args_opt.add_argument(
        "--find_first",
        help="If providing multiple protocol templates, stop when a perfect protocol "
        "match is found. (default: False)",
        action="store_true",
    )
    args_opt.add_argument(
        "--logs_dir",
        help="Directory for the logs will be written to. If the directory does not "
        "exist, it will be created. If not provided, the logs will be written into "
        "the current working directory. (default: None)",
        type=Path,
        default=Path(),
    )
    args_opt.add_argument(
        "--sub_label",
        help="When generating a tags file, use this to specify a custom "
        "subject_label. Not strictly necessary, as the contents of the PatientID "
        "field will also be included in subject_details portion of the tags file. "
        "(default: None)",
        type=str,
        default=None,
    )
    args_opt.add_argument(
        "--which_tags",
        help="Specifies in which situations the tags files should be generated. "
        "'all' will generate a tag file per protocol template, 'highest' will "
        "generate a tag file for only the highest (one or more) matches, while "
        "'none' will turn of the tag generation feature all together. (default: highest)",
        type=str,
        choices=["none", "highest", "all"],
        default="highest",
    )

    # General
    args_info = parser.add_argument_group("information arguments")
    args_info.add_argument(
        "--debug_level",
        help="Level of logging when running. Select 'DEBUG' to have the logs list "
        "each mismatched DICOM header field. (default: INFO)",
        choices=["INFO", "DEBUG"],
        default="INFO",
    )
    args_info.add_argument(
        "-v",
        "--version",
        help="Version",
        action="version",
        version=f"protocol_qc: version {__version__}",
    )
    args_info.add_argument(
        "-h", "--help", help="Show this help message and exit.", action="help"
    )

    return parser.parse_args(args)
