"""
Tests for custom logger
"""

import logging
from pathlib import Path

from protocol_qc.utils import cust_logging


def test_set_logging_dir(tmp_path):
    """Test creating the log directory"""

    dir_logs = Path(tmp_path) / "logging_dir"

    _ = cust_logging.set_logging_dir(dir_logs)

    assert dir_logs.is_dir()


def test_set_logging_dir_unspecified():
    """Test creating the log directory"""

    assert cust_logging.set_logging_dir(None) == Path()


def test_custom_logger(tmp_path):
    """Test setting up custom logger with log dir provided"""

    dir_logs = Path(tmp_path) / "logger_test1"
    dir_logs.mkdir()

    logger = cust_logging.custom_logger("test_logger1.json", dir_logs, logging.INFO)

    assert "logger_test1" in logger.handlers[0].baseFilename


def test_custom_logger_no_dir():
    """Test setting up custom logger without log dir provided"""

    cwd = Path.cwd()

    name_logger = Path("test_logger2.json")

    logger = cust_logging.custom_logger(name_logger.name, Path(), logging.INFO)

    assert cwd.name in logger.handlers[0].baseFilename

    name_logger = name_logger.with_suffix(".log")
    if name_logger.is_file():
        name_logger.unlink()


def test_custom_logger_summary():
    """Test setting up summary logger"""

    name_logger = Path("summary.json")

    logger = cust_logging.custom_logger(name_logger.name, Path(), logging.INFO)

    assert "summary" in logger.name

    name_logger = name_logger.with_suffix(".log")
    if name_logger.is_file():
        name_logger.unlink()
