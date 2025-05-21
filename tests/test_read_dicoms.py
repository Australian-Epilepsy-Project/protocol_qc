"""
Tests for read_dicoms.py
"""

import logging

import pytest

from protocol_qc import read_dicoms

logger = logging.getLogger()


def test_construct_classes(dicom_list):
    """Test constructing classes"""

    series = read_dicoms.construct_classes(dicom_list)

    assert len(series) == 8
    assert series[0].unique_label() == "1:T1w_Sag_AP-"
    assert series[0].num_files == 192
    assert series[1].unique_label() == "2:T1w_Sag_AP-"
    assert series[1].num_files == 192


def test_total_files(caplog, data_series):
    """Test calc total files"""

    caplog.set_level(logging.INFO)

    read_dicoms.number_of_files(data_series, logger)

    assert "Total DICOM files: 1987" in caplog.text


def test_find_unique_series(dicom_dir):
    """Test finding unique series"""

    series = read_dicoms.find_unique_series(dicom_dir, logger)

    assert len(series) == 8
    assert series[0].unique_label() == "1:T1w_Sag_AP-"
    assert series[0].num_files == 192
    assert series[1].unique_label() == "2:T1w_Sag_AP-"
    assert series[1].num_files == 192


def test_find_unique_series_no_dicoms(tmp_path):
    """Test finding nothing in empty dir"""

    dir_no_dicoms = tmp_path / "dir_no_dicoms/"
    dir_no_dicoms.mkdir()
    (dir_no_dicoms / "not_dicom.jpeg").touch()

    with pytest.raises(FileNotFoundError) as error:
        _ = read_dicoms.find_unique_series(dir_no_dicoms, logger)

    assert "Could not locate any DICOMS in: " in error.value.args[0]

    (dir_no_dicoms / "not_dicom.jpeg").unlink()
