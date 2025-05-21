"""
Conftest.py to store fixtures
"""

import json
import logging
from pathlib import Path

import pydicom
import pytest

from protocol_qc import build_templates, read_dicoms

logger = logging.getLogger()


# configs
@pytest.fixture(name="config_t1", scope="function")
def fixture_config_t1():
    """Basic protocol template containing only T1w templates"""

    template_prot = {
        "T1w": {
            "num_series": 2,
            "duplicates_allowed": False,
            "fields": {
                "SeriesDescription": {"value": "T1w", "comparison": "regex"},
                "SequenceName": {"value": "t1w_seq_name", "comparison": "exact"},
                "ScanOptions": {"value": ["IR", "WE"], "comparison": "exact"},
                "ScanningSequence": {"value": ["GR", "IR"], "comparison": "regex"},
                "SequenceVariant": {"value": ["SK", "SP", "MP"], "comparison": "exact"},
                "Rows": {"value": 256, "comparison": "exact"},
                "Columns": {"value": 256, "comparison": "exact"},
                "SAR": {"value": [0, 1], "comparison": "in_range"},
                "MagneticFieldStrength": {"value": [1, 3, 7], "comparison": "in_set"},
                "MRAcquisitionType": {"value": "3D", "comparison": "exact"},
            },
            "series": {
                "mag": {
                    "num_files": 192,
                    "fields": {
                        "ImageType": {
                            "value": ["ORIGINAL", "PRIMARY", "M", "ND"],
                            "comparison": "exact",
                        }
                    },
                },
                "mag_prenorm": {
                    "num_files": 192,
                    "fields": {
                        "ImageType": {
                            "value": ["ORIGINAL", "PRIMARY", "M", "ND", "NORM"],
                            "comparison": "exact",
                        }
                    },
                },
            },
        }
    }

    return template_prot


@pytest.fixture(name="config_t1_partial", scope="function")
def fixture_config_t1_partial(config_t1):
    """Basic protocol template containing only T1w templates that will
    partially match data"""

    # Alter some fields to enforce only a partial match
    config_t1["T1w"]["series"]["mag"]["fields"]["ImageType"] = {
        "value": "WRONG",
        "comparison": "exact",
    }

    return config_t1


@pytest.fixture(name="config_t1_duplicates_allow", scope="function")
def fixture_config_t1_duplicates_allow(config_t1):
    """Basic protocol template containing only T1w templates that allow duplicates"""

    config_t1["T1w"]["duplicates_allowed"] = True

    return config_t1


@pytest.fixture(name="config_t1_duplicates_exp", scope="function")
def fixture_config_t1_duplicates_exp(config_t1):
    """Basic protocol template containing only T1w templates that expect duplicates"""

    config_t1["T1w"]["duplicates_expected"] = 2
    config_t1["T1w"]["duplicates_allowed"] = True

    return config_t1


@pytest.fixture(name="config_flair")
def fixture_config_flair():
    """Basic protocol template containing only FLAIR templates"""

    template_prot = {
        "FLAIR": {
            "num_series": 2,
            "duplicates_allowed": False,
            "fields": {
                "SeriesDescription": {"value": "T2wFLAIR", "comparison": "regex"},
                "SequenceName": {"value": "flair_seq_name", "comparison": "exact"},
                "ScanOptions": {"value": ["IR", "PFP"], "comparison": "exact"},
                "ScanningSequence": {"value": ["SE", "IR"], "comparison": "regex"},
                "SequenceVariant": {"value": ["SK", "SP", "MP"], "comparison": "exact"},
                "Rows": {"value": 256, "comparison": "exact"},
                "Columns": {"value": 256, "comparison": "exact"},
                "SAR": {"value": [0, 1], "comparison": "in_range"},
                "MagneticFieldStrength": {"value": [1, 3, 7], "comparison": "in_set"},
            },
            "series": {
                "mag": {
                    "num_files": 192,
                    "fields": {
                        "ImageType": {
                            "value": ["ORIGINAL", "PRIMARY", "M", "ND", "NORM"],
                            "comparison": "exact",
                        }
                    },
                },
                "mag_fil": {
                    "num_files": 192,
                    "fields": {
                        "ImageType": {
                            "value": ["ORIGINAL", "PRIMARY", "M", "ND", "NORM", "FIL"],
                            "comparison": "exact",
                        }
                    },
                },
            },
        }
    }

    return template_prot


@pytest.fixture(name="config_fmri")
def fixture_config_fmri():
    """Basic protocol template containing only fMRI templates"""

    template_prot = {
        "fMRI": {
            "num_series": 4,
            "duplicates_allowed": False,
            "fields": {
                "SeriesDescription": {"value": "Pseudoword", "comparison": "regex"},
                "SequenceName": {"value": "fmri_seq_name", "comparison": "exact"},
                "ScanningSequence": {"value": "EP", "comparison": "exact"},
                "SequenceVariant": {"value": ["SK", "SS"], "comparison": "exact"},
                "ScanOptions": {"value": ["PFP", "FS", "EXT"], "comparison": "exact"},
                "Rows": {"value": 560, "comparison": "exact"},
                "Columns": {"value": 504, "comparison": "exact"},
            },
            "series": {
                "SBref": {
                    "num_files": 6,
                    "fields": {
                        "ImageComments": {
                            "value": "Single-band reference SENSE1+",
                            "comparison": "regex",
                        }
                    },
                },
                "mag": {
                    "num_files": 606,
                    "fields": {
                        "ImageType": {
                            "value": [
                                "ORIGINAL",
                                "PRIMARY",
                                "M",
                                "MB",
                                "TE",
                                "ND",
                                "NORM",
                                "MOSAIC",
                            ],
                            "comparison": "regex",
                        }
                    },
                },
                "phase": {
                    "num_files": 606,
                    "fields": {
                        "ImageType": {
                            "value": [
                                "ORIGINAL",
                                "PRIMARY",
                                "P",
                                "MB",
                                "TE",
                                "ND",
                                "MOSAIC",
                            ],
                            "comparison": "regex",
                        }
                    },
                },
                "PhysioLog": {
                    "num_files": 1,
                    "share_fields": False,
                    "fields": {
                        "SeriesDescription": {
                            "value": "Pseudoword",
                            "comparison": "regex",
                        },
                        "ImageType": {
                            "value": ["ORIGINAL", "PRIMARY", "RAWDATA", "PHYSIO"],
                            "comparison": "exact",
                        },
                    },
                },
            },
        },
    }

    return template_prot


@pytest.fixture(name="config_file_t1")
def fixture_config_file_t1(tmp_path, config_t1):
    """Test config file"""

    filename_config = tmp_path / "config_t1.json"

    with filename_config.open("w", encoding="utf-8") as out_config:
        json.dump(config_t1, out_config)

    return filename_config


@pytest.fixture(name="config_file_t1_duplicates")
def fixture_config_file_t1_duplicates(tmp_path, config_t1_duplicates_allow):
    """Test config file"""

    filename_config = tmp_path / "config_t1_duplicates_allow.json"

    with filename_config.open("w", encoding="utf-8") as out_config:
        json.dump(config_t1_duplicates_allow, out_config)

    return filename_config


@pytest.fixture(name="config_file_flair")
def fixture_config_file_flair(tmp_path, config_flair):
    """Test config file"""

    filename_config = tmp_path / "config_flair.json"

    with filename_config.open("w", encoding="utf-8") as out_config:
        json.dump(config_flair, out_config)

    return filename_config


@pytest.fixture(name="config_file_fmri")
def fixture_config_file_fmri(tmp_path, config_fmri):
    """Test config file"""

    filename_config = tmp_path / "config_fmri.json"

    with filename_config.open("w", encoding="utf-8") as out_config:
        json.dump(config_fmri, out_config)

    return filename_config


@pytest.fixture(name="config_file_missing_fmri")
def fixture_config_file_missing_fmri(tmp_path, config_t1, config_flair):
    """Test config file"""

    filename_config = tmp_path / "config_missing_fmri.json"

    all_configs = {**config_t1, **config_flair}

    with filename_config.open("w", encoding="utf-8") as out_config:
        json.dump(all_configs, out_config)

    return filename_config


@pytest.fixture(name="config_file_all_partial_t1")
def fixture_config_file_all_partial_t1(
    tmp_path, config_t1_partial, config_flair, config_fmri
):
    """Test config with partial t1 match"""

    filename_config = tmp_path / "config_all_partial_t1.json"

    all_configs = {**config_t1_partial, **config_flair, **config_fmri}

    return (filename_config.name, all_configs)


@pytest.fixture(name="config_file_all")
def fixture_config_file_all(tmp_path, config_t1, config_flair, config_fmri):
    """Test config file"""

    filename_config = tmp_path / "config_all.json"

    all_configs = {**config_t1, **config_flair, **config_fmri}

    with filename_config.open("w", encoding="utf-8") as out_config:
        json.dump(all_configs, out_config)

    return filename_config


@pytest.fixture(name="config_file_all_duplicates_allow")
def fixture_config_file_all_duplicates_allow(
    tmp_path, config_t1_duplicates_allow, config_flair, config_fmri
):
    """Test config file"""

    filename_config = tmp_path / "config_all_duplicates_allow.json"

    all_configs = {**config_t1_duplicates_allow, **config_flair, **config_fmri}

    with filename_config.open("w", encoding="utf-8") as out_config:
        json.dump(all_configs, out_config)

    return filename_config


@pytest.fixture(name="config_dir")
def fixture_config_dir(tmpdir, config_t1, config_flair):
    """Test directory of config files"""

    config_dir = tmpdir / "configs"
    config_dir.mkdir()

    filename_config_t1 = config_dir / "config_t1.json"
    filename_config_flair = config_dir / "config_flair.json"

    with filename_config_t1.open("w", encoding="utf-8") as out_config:
        json.dump(config_t1, out_config)

    with filename_config_flair.open("w", encoding="utf-8") as out_config:
        json.dump(config_flair, out_config)

    return Path(config_dir)


# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
@pytest.fixture(name="dicom_dir", scope="session")
def fixture_dicom_dir(tmp_path_factory):
    """Create a set of dummy DICOMS for testing"""

    dicom_dir = tmp_path_factory.mktemp("dicom_dir")

    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.UID("1.2.3")
    file_meta.ImplementationClassUID = pydicom.uid.UID("1.2.3.4")

    # T1w
    for i in range(0, 192):
        # mag
        name_t1_mag = dicom_dir / f"t1_mag_{i}.dcm"
        dicom_t1_mag = pydicom.dataset.FileDataset(
            name_t1_mag.name, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_t1_mag.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_t1_mag.SeriesInstanceUID = "1"
        dicom_t1_mag.SeriesDescription = "T1w_Sag_AP-"
        dicom_t1_mag.SeriesNumber = "1"
        dicom_t1_mag.SequenceName = "t1w_seq_name"
        dicom_t1_mag.ScanOptions = ["IR", "WE"]
        dicom_t1_mag.ScanningSequence = ["GR", "IR"]
        dicom_t1_mag.SequenceVariant = ["SK", "SP", "MP"]
        dicom_t1_mag.Rows = 256
        dicom_t1_mag.Columns = 256
        dicom_t1_mag.ImageType = ["ORIGINAL", "PRIMARY", "M", "ND"]
        dicom_t1_mag.SAR = 0.00123
        dicom_t1_mag.MagneticFieldStrength = 3
        dicom_t1_mag.MRAcquisitionType = "3D"
        dicom_t1_mag.save_as(name_t1_mag)
        # mag_prenorm
        name_t1_mag_prenorm = dicom_dir / f"t1_mag_prenorm_{i}.dcm"
        dicom_t1_mag_prenorm = pydicom.dataset.FileDataset(
            name_t1_mag_prenorm, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_t1_mag_prenorm.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_t1_mag_prenorm.SeriesInstanceUID = "2"
        dicom_t1_mag_prenorm.SeriesDescription = "T1w_Sag_AP-"
        dicom_t1_mag_prenorm.SeriesNumber = "2"
        dicom_t1_mag_prenorm.SequenceName = "t1w_seq_name"
        dicom_t1_mag_prenorm.ScanOptions = ["IR", "WE"]
        dicom_t1_mag_prenorm.ScanningSequence = ["GR", "IR"]
        dicom_t1_mag_prenorm.SequenceVariant = ["SK", "SP", "MP"]
        dicom_t1_mag_prenorm.Rows = 256
        dicom_t1_mag_prenorm.Columns = 256
        dicom_t1_mag_prenorm.ImageType = ["ORIGINAL", "PRIMARY", "M", "ND", "NORM"]
        dicom_t1_mag_prenorm.SAR = 0.00123
        dicom_t1_mag_prenorm.MagneticFieldStrength = 3
        dicom_t1_mag_prenorm.MRAcquisitionType = "3D"
        dicom_t1_mag_prenorm.save_as(name_t1_mag_prenorm)

    # FLAIR
    for i in range(0, 192):
        # mag
        name_flair_mag = dicom_dir / f"flair_mag_{i}.dcm"
        dicom_flair_mag = pydicom.dataset.FileDataset(
            name_flair_mag.name, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_flair_mag.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_flair_mag.SeriesInstanceUID = "3"
        dicom_flair_mag.SeriesDescription = "T2wFLAIR-ORIG"
        dicom_flair_mag.SeriesNumber = "3"
        dicom_flair_mag.SequenceName = "flair_seq_name"
        dicom_flair_mag.ScanOptions = ["IR", "PFP"]
        dicom_flair_mag.ScanningSequence = ["SE", "IR"]
        dicom_flair_mag.SequenceVariant = ["SK", "SP", "MP"]
        dicom_flair_mag.Rows = 256
        dicom_flair_mag.Columns = 256
        dicom_flair_mag.ImageType = ["ORIGINAL", "PRIMARY", "M", "ND", "NORM"]
        dicom_flair_mag.SAR = 0.00123
        dicom_flair_mag.MagneticFieldStrength = 3
        dicom_flair_mag.save_as(name_flair_mag)
        # mag_prenorm
        name_flair_mag_prenorm = dicom_dir / f"flair_mag_prenorm_{i}.dcm"
        dicom_flair_mag_prenorm = pydicom.dataset.FileDataset(
            name_flair_mag_prenorm, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_flair_mag_prenorm.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_flair_mag_prenorm.SeriesInstanceUID = "4"
        dicom_flair_mag_prenorm.SeriesDescription = "T2wFLAIR-"
        dicom_flair_mag_prenorm.SeriesNumber = "4"
        dicom_flair_mag_prenorm.SequenceName = "flair_seq_name"
        dicom_flair_mag_prenorm.ScanOptions = ["IR", "PFP"]
        dicom_flair_mag_prenorm.ScanningSequence = ["SE", "IR"]
        dicom_flair_mag_prenorm.SequenceVariant = ["SK", "SP", "MP"]
        dicom_flair_mag_prenorm.Rows = 256
        dicom_flair_mag_prenorm.Columns = 256
        dicom_flair_mag_prenorm.ImageType = [
            "ORIGINAL",
            "PRIMARY",
            "M",
            "ND",
            "NORM",
            "FIL",
        ]
        dicom_flair_mag_prenorm.SAR = 0.00123
        dicom_flair_mag_prenorm.MagneticFieldStrength = 3
        dicom_flair_mag_prenorm.save_as(name_flair_mag_prenorm)

    # fMRI
    for i in range(0, 6):
        # mag
        name_fmri_sbref = dicom_dir / f"fmri_sbref_{i}.dcm"
        dicom_fmri_sbref = pydicom.dataset.FileDataset(
            name_fmri_sbref.name, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_fmri_sbref.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_fmri_sbref.SeriesInstanceUID = "5"
        dicom_fmri_sbref.SeriesDescription = "fMRI_Pseudoword-SBref"
        dicom_fmri_sbref.SeriesNumber = "5"
        dicom_fmri_sbref.SequenceName = "fmri_seq_name"
        dicom_fmri_sbref.ScanOptions = ["PFP", "FS", "EXT"]
        dicom_fmri_sbref.ScanningSequence = "EP"
        dicom_fmri_sbref.SequenceVariant = ["SK", "SS"]
        dicom_fmri_sbref.Rows = 560
        dicom_fmri_sbref.Columns = 504
        dicom_fmri_sbref.ImageComments = "Single-band reference SENSE1+"
        dicom_fmri_sbref.save_as(name_fmri_sbref)
    for i in range(0, 606):
        # mag
        name_fmri_mag = dicom_dir / f"fmri_mag_{i}.dcm"
        dicom_fmri_mag = pydicom.dataset.FileDataset(
            name_fmri_mag.name, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_fmri_mag.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_fmri_mag.SeriesInstanceUID = "6"
        dicom_fmri_mag.SeriesDescription = "fMRI_Pseudoword-"
        dicom_fmri_mag.SeriesNumber = "6"
        dicom_fmri_mag.SequenceName = "fmri_seq_name"
        dicom_fmri_mag.ScanOptions = ["PFP", "FS", "EXT"]
        dicom_fmri_mag.ScanningSequence = "EP"
        dicom_fmri_mag.SequenceVariant = ["SK", "SS"]
        dicom_fmri_mag.Rows = 560
        dicom_fmri_mag.Columns = 504
        dicom_fmri_mag.ImageType = [
            "ORIGINAL",
            "PRIMARY",
            "M",
            "MB",
            "TE",
            "ND",
            "NORM",
            "MOSAIC",
        ]
        dicom_fmri_mag.save_as(name_fmri_mag)
        # phase
        name_fmri_phase = dicom_dir / f"fmri_phase_{i}.dcm"
        dicom_fmri_phase = pydicom.dataset.FileDataset(
            name_fmri_phase, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_fmri_phase.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_fmri_phase.SeriesInstanceUID = "7"
        dicom_fmri_phase.SeriesDescription = "fMRI_Pseudoword-"
        dicom_fmri_phase.SeriesNumber = "7"
        dicom_fmri_phase.SequenceName = "fmri_seq_name"
        dicom_fmri_phase.ScanOptions = ["PFP", "FS", "EXT"]
        dicom_fmri_phase.ScanningSequence = "EP"
        dicom_fmri_phase.SequenceVariant = ["SK", "SS"]
        dicom_fmri_phase.Rows = 560
        dicom_fmri_phase.Columns = 504
        dicom_fmri_phase.ImageType = [
            "ORIGINAL",
            "PRIMARY",
            "P",
            "MB",
            "TE",
            "ND",
            "MOSAIC",
        ]
        dicom_fmri_phase.save_as(name_fmri_phase)
    # PhysioLog
    name_fmri_physiolog = dicom_dir / "fmri_physiolog.dcm"
    dicom_fmri_physiolog = pydicom.dataset.FileDataset(
        name_fmri_physiolog, {}, file_meta=file_meta, preamble=b"\0" * 128
    )
    dicom_fmri_physiolog.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
    dicom_fmri_physiolog.SeriesInstanceUID = "8"
    dicom_fmri_physiolog.SeriesDescription = "fMRI_Pseudoword-PhysioLog"
    dicom_fmri_physiolog.SeriesNumber = "8"
    dicom_fmri_physiolog.ImageType = ["ORIGINAL", "PRIMARY", "RAWDATA", "PHYSIO"]
    dicom_fmri_physiolog.save_as(name_fmri_physiolog)

    return dicom_dir


@pytest.fixture(name="dicom_dir_duplicates", scope="function")
def fixture_dicom_dir_duplicates(tmp_path):
    """Create a set of dummy duplicate DICOMS for testing"""

    dicom_dir = tmp_path / "dicom_dupes"
    dicom_dir.mkdir()

    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.UID("1.2.3")
    file_meta.ImplementationClassUID = pydicom.uid.UID("1.2.3.4")

    # T1w
    for i in range(0, 192):
        # mag
        name_t1_mag = dicom_dir / f"t1_mag_duplicate_{i}.dcm"
        dicom_t1_mag = pydicom.dataset.FileDataset(
            name_t1_mag.name, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_t1_mag.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_t1_mag.SeriesInstanceUID = "9"
        dicom_t1_mag.SeriesDescription = "T1w_Sag_AP-REPEAT"
        dicom_t1_mag.SeriesNumber = "9"
        dicom_t1_mag.SequenceName = "t1w_seq_name"
        dicom_t1_mag.ScanOptions = ["IR", "WE"]
        dicom_t1_mag.ScanningSequence = ["GR", "IR"]
        dicom_t1_mag.SequenceVariant = ["SK", "SP", "MP"]
        dicom_t1_mag.Rows = 256
        dicom_t1_mag.Columns = 256
        dicom_t1_mag.ImageType = ["ORIGINAL", "PRIMARY", "M", "ND"]
        dicom_t1_mag.SAR = 0.00123
        dicom_t1_mag.MagneticFieldStrength = 3
        dicom_t1_mag.MRAcquisitionType = "3D"
        dicom_t1_mag.save_as(name_t1_mag)
        # mag_prenorm
        name_t1_mag_prenorm = dicom_dir / f"t1_mag_prenorm_duplicate_{i}.dcm"
        dicom_t1_mag_prenorm = pydicom.dataset.FileDataset(
            name_t1_mag_prenorm, {}, file_meta=file_meta, preamble=b"\0" * 128
        )
        dicom_t1_mag_prenorm.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
        dicom_t1_mag_prenorm.SeriesInstanceUID = "10"
        dicom_t1_mag_prenorm.SeriesDescription = "T1w_Sag_AP-REPEAT"
        dicom_t1_mag_prenorm.SeriesNumber = "10"
        dicom_t1_mag_prenorm.SequenceName = "t1w_seq_name"
        dicom_t1_mag_prenorm.ScanOptions = ["IR", "WE"]
        dicom_t1_mag_prenorm.ScanningSequence = ["GR", "IR"]
        dicom_t1_mag_prenorm.SequenceVariant = ["SK", "SP", "MP"]
        dicom_t1_mag_prenorm.Rows = 256
        dicom_t1_mag_prenorm.Columns = 256
        dicom_t1_mag_prenorm.ImageType = ["ORIGINAL", "PRIMARY", "M", "ND", "NORM"]
        dicom_t1_mag_prenorm.SAR = 0.00123
        dicom_t1_mag_prenorm.MagneticFieldStrength = 3
        dicom_t1_mag_prenorm.MRAcquisitionType = "3D"
        dicom_t1_mag_prenorm.save_as(name_t1_mag_prenorm)

    return dicom_dir


@pytest.fixture(name="dicom_list", scope="function")
def fixture_dicom_list(dicom_dir):
    """Return dictionary of dicoms in directory"""

    dicoms = {}

    for dicom in dicom_dir.rglob("*.dcm"):
        dicom_data = pydicom.dcmread(dicom)
        if dicom_data.SeriesInstanceUID in dicoms:
            dicoms[dicom_data.SeriesInstanceUID]["files"] += 1
        else:
            dicoms[dicom_data.SeriesInstanceUID] = {
                "files": 1,
                "path": dicom.as_posix(),
            }

    return dicoms


@pytest.fixture(name="data_series", scope="function")
def fixture_data_series(dicom_list):
    """Return list of unique DataSeries"""

    return read_dicoms.construct_classes(dicom_list)


@pytest.fixture(name="data_series_duplicates", scope="function")
def fixture_data_series_duplicates(dicom_dir, dicom_dir_duplicates):
    """Return dictionary of dicoms with duplicates"""

    dicoms = {}

    for dicom in dicom_dir.rglob("*.dcm"):
        dicom_data = pydicom.dcmread(dicom)
        if dicom_data.SeriesInstanceUID in dicoms:
            dicoms[dicom_data.SeriesInstanceUID]["files"] += 1
        else:
            dicoms[dicom_data.SeriesInstanceUID] = {
                "files": 1,
                "path": dicom.as_posix(),
            }

    for dicom in dicom_dir_duplicates.rglob("*.dcm"):
        dicom_data = pydicom.dcmread(dicom)
        if dicom_data.SeriesInstanceUID in dicoms:
            dicoms[dicom_data.SeriesInstanceUID]["files"] += 1
        else:
            dicoms[dicom_data.SeriesInstanceUID] = {
                "files": 1,
                "path": dicom.as_posix(),
            }

    return read_dicoms.construct_classes(dicoms)


@pytest.fixture(name="t1_protocol", scope="function")
def fixture_t1_protocol(config_t1):
    """Return template protocol"""

    return build_templates.build_templates(
        ("config_t1.json", config_t1), 0.9, "mock_id", logger
    )


@pytest.fixture(name="protocol_all", scope="function")
def fixture_protocol_all(config_t1, config_flair, config_fmri):
    """Return template protocol with all three acquisitions"""

    return build_templates.build_templates(
        ("config_all.json", {**config_t1, **config_flair, **config_fmri}),
        0.9,
        "mock_id",
        logger,
    )


@pytest.fixture(name="protocol_all_duplicates_allow", scope="function")
def fixture_protocol_all_duplicates_allow(
    config_t1_duplicates_allow, config_flair, config_fmri
):
    """Return template protocol with all three acquisitions"""

    return build_templates.build_templates(
        (
            "config_all_t1_duplicates_allow.json",
            {**config_t1_duplicates_allow, **config_flair, **config_fmri},
        ),
        0.9,
        "mock_id",
        logger,
    )


@pytest.fixture(name="protocol_all_duplicates_exp", scope="function")
def fixture_protocol_all_duplicates_exp(
    config_t1_duplicates_exp, config_flair, config_fmri
):
    """Return template protocol with all three acquisitions"""

    return build_templates.build_templates(
        (
            "config_all_t1_duplicates_exp.json",
            {**config_t1_duplicates_exp, **config_flair, **config_fmri},
        ),
        0.9,
        "mock_id",
        logger,
    )


@pytest.fixture(name="protocol_missing_fmri", scope="function")
def fixture_protocol_missing_fmri(config_t1, config_flair):
    """Return template protocol without fmri templates"""

    return build_templates.build_templates(
        ("config_missing_fmri.json", {**config_t1, **config_flair}),
        0.9,
        "mock_id",
        logger,
    )


@pytest.fixture(name="protocol_all_partial_t1", scope="function")
def fixture_protocol_all_partial_t1(config_t1_partial, config_flair, config_fmri):
    """Return template protocol without fmri templates"""

    return build_templates.build_templates(
        (
            "config_all_partial_t1",
            {**config_t1_partial, **config_flair, **config_fmri},
        ),
        0.9,
        "mock_id",
        logger,
    )
