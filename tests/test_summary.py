"""
Tests for summary.py
"""

import logging

from protocol_qc import summary

logger = logging.getLogger()


def test_summarise_protocol_matches_single_prot(
    caplog, mocker, data_series, protocol_all
):
    """Test summarising single protocol"""

    caplog.set_level(logging.DEBUG)

    protocol_all.compare_protocol(data_series)

    print_exact_match_mocked = mocker.patch("protocol_qc.summary.print_exact_match")
    print_exact_match_mocked.return_value = 0

    summary.summarise_protocol_matches([protocol_all], 0.8, logger)

    assert "Summarising protocol matches" in caplog.text
    assert "is missing data" not in caplog.text
    assert "acquisitions was unmatched" not in caplog.text
    assert "unexpeceted duplicates" not in caplog.text
    assert "extra series were detected" not in caplog.text
    assert "allowed duplicates" not in caplog.text


def test_summarise_protocol_matches_single_prot_has_issues(
    caplog, mocker, data_series_duplicates, protocol_missing_fmri
):
    """Test summarising single protocol that has issues"""

    caplog.set_level(logging.DEBUG)

    # Set num files to an incorrect value
    data_series_duplicates[3].num_files = 1

    protocol_missing_fmri.compare_protocol(data_series_duplicates)

    print_exact_match_mocked = mocker.patch("protocol_qc.summary.print_exact_match")
    print_exact_match_mocked.return_value = 0

    summary.summarise_protocol_matches([protocol_missing_fmri], 0.8, logger)

    assert "Summarising protocol matches" in caplog.text
    assert "(MISSING DATA)" in caplog.text
    assert "acquisitions was unmatched" not in caplog.text
    assert "wrong number of duplicates for one or more" in caplog.text
    assert "extra series were detected (unexpected)" in caplog.text
    assert "allowed duplicates" not in caplog.text


def test_print_exact_match(caplog, data_series, protocol_all, protocol_missing_fmri):
    """Testing printing exact match"""

    caplog.set_level(logging.DEBUG)

    protocol_all.compare_protocol(data_series)
    protocol_missing_fmri.compare_protocol(data_series)
    protocol_missing_fmri.has_issue = True

    exit_code = summary.print_exact_match([protocol_all, protocol_missing_fmri], logger)

    assert exit_code == 0
    assert "The following template was matched:" in caplog.text
    assert "allowed duplicates" not in caplog.text


def test_print_exact_match_multiple_matches(
    caplog, data_series, protocol_all, protocol_missing_fmri
):
    """Testing printing with multiple matches"""

    caplog.set_level(logging.DEBUG)

    protocol_all.compare_protocol(data_series)
    protocol_missing_fmri.compare_protocol(data_series)

    exit_code = summary.print_exact_match([protocol_all, protocol_missing_fmri], logger)

    assert exit_code == 1
    assert "Multiple templates were matched" in caplog.text


def test_print_exact_match_no_matches(caplog, data_series, protocol_missing_fmri):
    """Testing printing with no matches"""

    caplog.set_level(logging.DEBUG)

    protocol_missing_fmri.compare_protocol(data_series)
    protocol_missing_fmri.has_issue = True

    exit_code = summary.print_exact_match([protocol_missing_fmri], logger)

    assert exit_code == 2
    assert "No templates were matched" in caplog.text
