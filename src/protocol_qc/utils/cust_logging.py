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
Custom logging to enable individual log files per user protocol template.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def set_logging_dir(log_dir: Path | None) -> Path:
    """
    Set directory to store logs, if specified by user.

    Parameters
    ----------
    log_dir
        User specified directory to store logs in (can be unset).

    Returns
    -------
        Directory to store logs in
    """

    if log_dir is not None:
        if not log_dir.is_dir():
            log_dir.mkdir(parents=False, exist_ok=True)
        return log_dir

    return Path()


def custom_logger(
    logger_name: str,
    log_dir: Path,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Return a custom logger with the given name and level. If the user specified
    a log directory, the directory will be created, if it doesn't exist, and
    logs will be written into it, otherwise logs are written into the current
    working directory.

    Parameters
    ----------
    logger_name
        Name of logger.
    log_dir
        Directory to store logs in or None.
    level
        Level of logging (INFO, DEBUG).

    Returns
    -------
        Custom logger
    """

    # Remove json suffix
    if "json" in logger_name:
        logger_name = logger_name[:-5]

    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    format_string: str = "%(levelname)s %(message)s"
    format_date: str = "%H:%M"
    log_format = logging.Formatter(format_string, format_date)

    if "summary" in logger_name and not logging.getLogger().hasHandlers():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_dir / (logger_name + ".log"), mode="w")

    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger
