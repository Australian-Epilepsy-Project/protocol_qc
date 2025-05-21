"""
Tests for build_templates.py
"""

import json
import logging

from protocol_qc import build_templates

logger = logging.getLogger()


def test_duplicates_settings_noallowed(config_t1):
    """Test duplicates not allowed set"""

    allow, exp = build_templates.duplicates_settings(config_t1["T1w"])

    assert allow is False
    assert exp == 0


def test_duplicates_settings_allowed(config_t1):
    """Test only duplicated allowed set"""

    config_t1["T1w"]["duplicates_allowed"] = True

    allow, exp = build_templates.duplicates_settings(config_t1["T1w"])

    assert allow is True
    assert exp == 0


def test_duplicates_settings_none_set(config_t1):
    """Test defaults are set correctly"""

    config_t1["T1w"].pop("duplicates_allowed")

    allow, exp = build_templates.duplicates_settings(config_t1["T1w"])

    assert allow is False
    assert exp == 0


def test_duplicates_settings_exp_set(config_t1):
    """Test only expected explicitly set"""

    config_t1["T1w"].pop("duplicates_allowed")
    config_t1["T1w"]["duplicates_expected"] = 2

    allow, exp = build_templates.duplicates_settings(config_t1["T1w"])

    assert allow is True
    assert exp == 2


def test_extract_fields_no_share(config_t1):
    """Test series not sharing fields"""

    config_t1["T1w"]["series"]["mag"]["share_fields"] = False

    series = build_templates.set_fields(
        {}, config_t1["T1w"], config_t1["T1w"]["series"]["mag"]
    )

    # Assert fields at the acquisition level were not included
    assert series.get("SeriesDescription", None) is None


def test_extract_fields_share(config_t1):
    """Test series sharing fields"""

    config_t1["T1w"]["series"]["mag"]["share_fields"] = True

    series = build_templates.set_fields(
        {}, config_t1["T1w"], config_t1["T1w"]["series"]["mag"]
    )

    # Assert fields at the acquisition level were not included
    assert series["fields"]["SeriesDescription"]["value"] == "T1w"


def test_extract_fields_share_unset(config_t1):
    """Test no share_fields key being set"""

    series = build_templates.set_fields(
        {}, config_t1["T1w"], config_t1["T1w"]["series"]["mag"]
    )

    # Assert fields at the acquisition level were not included
    assert series["fields"]["SeriesDescription"]["value"] == "T1w"


def test_get_num_files_set(config_t1):
    """Test getting number of files when set"""

    num_files = build_templates.get_num_files(config_t1["T1w"]["series"]["mag"])

    assert num_files == 192


def test_get_num_files_unset(config_t1):
    """Test getting number of files when set"""

    config_t1["T1w"]["series"]["mag"].pop("num_files")

    num_files = build_templates.get_num_files(config_t1["T1w"]["series"]["mag"])

    assert num_files is None


def test_build_templates(config_file_t1):
    """Test creating T1w acquisition template"""

    with config_file_t1.open("r", encoding="utf-8") as in_config:
        template = json.load(in_config)

    temp_prot = build_templates.build_templates(
        (config_file_t1.name, template), 0.9, "mock_id", logger
    )

    # Assert all attributes have been set as expected
    assert temp_prot.name == "config_t1.json"
    assert temp_prot.score == 0
    assert temp_prot.incomplete_data is False
    assert temp_prot.missing_series is False
    assert temp_prot.extra_series == 0
    assert temp_prot.duplicates_allowed is False
    assert temp_prot.duplicates_unexpected is False
    assert temp_prot.duplicates_expected is False
    assert temp_prot.has_issue is False
