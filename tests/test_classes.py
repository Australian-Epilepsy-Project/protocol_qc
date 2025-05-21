"""
Tests for classes.
"""

import logging

import pydicom
import pytest

from protocol_qc.classes.dataseries import DataSeries
from protocol_qc.match_statuses import MatchStatus

logger = logging.getLogger()


def test_data_series_class(dicom_dir):
    """Test the DataSeries class"""

    dicoms = list(dicom_dir.rglob("*dcm"))

    dicoms.sort()

    data_series = DataSeries(pydicom.dcmread(dicoms[0]), 192, dicoms[0])

    assert "192 file(s)" in str(data_series)
    assert "3:T2wFLAIR-ORIG" in data_series.unique_label()


def test_template_series_methods(dicom_dir, t1_protocol):
    """Tests for individual methods from TemplateSeries"""

    dicoms = list(dicom_dir.rglob("*dcm"))

    # Only look at T1w series
    dicoms = [x for x in dicoms if "t1" in str(x)]

    dicoms.sort(key=lambda x: x.name.split(":")[0])

    data_series_1 = DataSeries(pydicom.dcmread(dicoms[0]), 192, dicoms[0])
    data_series_2 = DataSeries(pydicom.dcmread(dicoms[192]), 191, dicoms[1])

    template_acqs_1 = t1_protocol.template_acqs[0]
    temp_series_1 = template_acqs_1.template_series[0]
    temp_series_2 = template_acqs_1.template_series[1]

    assert temp_series_1.similar_series_names(data_series_1) is True
    assert temp_series_2.similar_series_names(data_series_2) is True

    assert not isinstance(
        temp_series_1.format_header_field(data_series_1.data.SeriesDescription), list
    )
    assert isinstance(
        temp_series_1.format_header_field(data_series_1.data.ImageType), list
    )

    assert len(temp_series_1.series_matches) == 0
    temp_series_1.compare_with_data_series(data_series_1)
    assert len(temp_series_1.series_matches) == 1
    assert temp_series_1.series_matches[0].score == 1.0

    temp_series_1.compare_with_data_series(data_series_2)
    assert temp_series_1.series_matches[1].score == pytest.approx(0.909090909)

    assert temp_series_1.is_series_complete(data_series_1) is True
    assert temp_series_1.is_series_complete(data_series_2) is False

    assert temp_series_1.compare_header_fields(data_series_1.data) == 1.0
    assert temp_series_1.compare_header_fields(data_series_2.data) == pytest.approx(
        0.909090909
    )


def test_prot_match(data_series, protocol_all):
    """Test protocol match. Only use T1w series"""

    assert protocol_all.score == 0
    assert (
        protocol_all.get_template_acquisitions()[0].match_status is MatchStatus.UNKNOWN
    )

    protocol_all.compare_protocol(data_series)

    assert protocol_all.get_template_acquisitions()[0].match_status is MatchStatus.MATCH

    assert protocol_all.score == 1.0
    assert protocol_all.incomplete_data is False
    assert protocol_all.missing_series is False
    assert protocol_all.extra_series == 0


def test_prot_match_extra_series(data_series, protocol_missing_fmri):
    """Test protocol match when extra series present"""

    protocol_missing_fmri.compare_protocol(data_series)

    assert (
        protocol_missing_fmri.get_template_acquisitions()[0].match_status
        is MatchStatus.MATCH
    )

    assert protocol_missing_fmri.score == 1.0
    assert protocol_missing_fmri.incomplete_data is False
    assert protocol_missing_fmri.missing_series is False
    assert protocol_missing_fmri.extra_series == 4


def test_prot_match_missing_series_incomplete(data_series, protocol_all):
    """Test protocol match with missing acquisition"""

    # Ignore fMRI data
    data_series_bad = data_series[:-4]

    # Set num files to an incorrect value
    data_series_bad[3].num_files = 1

    protocol_all.compare_protocol(data_series_bad)

    assert protocol_all.get_template_acquisitions()[-1].name == "fMRI"
    assert (
        protocol_all.get_template_acquisitions()[-1].match_status is MatchStatus.NOMATCH
    )

    assert protocol_all.score == pytest.approx(0.66666666666)
    assert protocol_all.incomplete_data is True
    assert protocol_all.missing_series is True
    assert protocol_all.extra_series == 0


def test_prot_match_duplicates_unexp(data_series_duplicates, protocol_all):
    """Test protocol match with missing acquisition"""

    protocol_all.compare_protocol(data_series_duplicates)

    assert protocol_all.get_template_acquisitions()[0].name == "T1w"
    assert (
        protocol_all.get_template_acquisitions()[0].match_status
        is MatchStatus.DUPES_UNEXP
    )

    assert protocol_all.score == 1.0
    assert protocol_all.incomplete_data is False
    assert protocol_all.missing_series is False
    assert protocol_all.extra_series == 0


def test_prot_match_duplicates_exp(data_series_duplicates, protocol_all_duplicates_exp):
    """Test protocol match with expected duplicates"""

    protocol_all_duplicates_exp.compare_protocol(data_series_duplicates)

    assert protocol_all_duplicates_exp.get_template_acquisitions()[0].name == "T1w"
    assert (
        protocol_all_duplicates_exp.get_template_acquisitions()[0].match_status
        is MatchStatus.DUPES_EXP
    )

    assert protocol_all_duplicates_exp.score == 1.0
    assert protocol_all_duplicates_exp.incomplete_data is False
    assert protocol_all_duplicates_exp.missing_series is False
    assert protocol_all_duplicates_exp.extra_series == 0


def test_prot_match_duplicates_allow(
    data_series_duplicates, protocol_all_duplicates_allow
):
    """Test protocol match with expected duplicates"""

    protocol_all_duplicates_allow.compare_protocol(data_series_duplicates)

    assert (
        protocol_all_duplicates_allow.get_template_acquisitions()[0].match_status
        is MatchStatus.DUPES_ALLOW
    )

    assert protocol_all_duplicates_allow.score == 1.0
    assert protocol_all_duplicates_allow.incomplete_data is False
    assert protocol_all_duplicates_allow.missing_series is False
    assert protocol_all_duplicates_allow.extra_series == 0


def test_prot_empty(protocol_all):
    """Test empty protocol"""

    protocol_all.template_acqs = []

    assert protocol_all.not_empty() is False


def test_print_prot_status(data_series, protocol_all):
    """Test printing protocol status"""

    protocol_all.compare_protocol(data_series)
