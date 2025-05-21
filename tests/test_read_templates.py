"""
Test for configs.py
"""

import logging
from pathlib import Path

import pytest

from protocol_qc import read_templates

logger = logging.getLogger()


def test_get_configs_file(caplog, config_file_t1):
    """Test reading in single config"""

    caplog.set_level(logging.INFO)

    user_configs = read_templates.get_templates(config_file_t1, logger)

    assert "T1w" in user_configs[0][1]


def test_get_configs_dir(config_dir):
    """Test reading in multiple configs"""

    user_configs = read_templates.get_templates(config_dir, logger)

    assert len(user_configs) == 2
    assert user_configs[0][0] == "config_flair.json"


def test_get_configs_file_fail():
    """Test failing to read in single config"""

    path_bad = Path("/no_n/E_config/here.json")

    with pytest.raises(FileNotFoundError):
        _ = read_templates.get_templates(path_bad, logger)


def test_get_configs_dir_fail(config_dir):
    """Test failing to read in single config"""

    # Remove json files from directory
    for config in config_dir.glob("*json"):
        config.unlink()

    with pytest.raises(FileNotFoundError):
        _ = read_templates.get_templates(config_dir, logger)


def test_get_configs_not_json(caplog):
    """Test reading in single config"""

    caplog.set_level(logging.INFO)

    config_not_json = Path("not_a_json.jpeg")
    config_not_json.touch()

    with pytest.raises(FileNotFoundError) as error:
        _ = read_templates.get_templates(config_not_json, logger)

    assert "not a json" in error.value.args[0]

    config_not_json.unlink()
