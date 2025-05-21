# protocol_qc: A MRI protocol quality control tool

[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

## Overview

`protocol_qc` is a Python package that aims to allow one to validate a DICOM study against a predefined template file containing key protocol parameters,
primarily via validation of DICOM header fields.
An overall matching score is calculated for each protocol template, along with any additional information relating to missing/extra series, as well as missing data (i.e., missing slices).

**Terminology**

The follow definitions are used by `protocol_qc`.
- *series*: One or more DICOMs with the same SeriesUID.
- *acquisitions*: One or more DICOM *series* logically grouped together. E.g., magnitude and phase components from a
  single scan, or, for functional scans the resulting single-band reference, magnitude and phase DICOM *series*.
- *protocol*: A group of *acquisitions*.

Note: `protocol_qc` is very much still under development, and therefore one should be aware of its [limitations](#limitations).

## Inputs

As input, one, or more, user defined template files must be provided.
For specification details see the template introduction [here](/docs/building_a_template.md).

## Outputs

A collection of logs will be generated during the assessment process.
A summary log contains information about the DICOM data (number of series, slices etc),
as well as a brief summary of all protocol template matches.
Additionally, individual logs for each protocol template are generated and contain detailed information about the matching procedure.

Lastly, a json file containing basic information about the protocol matching can be generated for each template protocol.
This so-called `tags` file will be created in the same location as the logs. The name of tags file will follow `<patient_identifier>_tags_<protocol_template_filename>.json`, where `<patient_identifier>` can be set with the CLI argument `sub_label`, otherwise it will default to the content in the DICOM header field 'PatientID'.
These files contain basic information such as the matching score, at the series, acquisition and protocol level,
as well as to which data series the template series were matched.
Additional `custom_tags` can be specified via the template. See [here](/docs/building_a_template.md) for more details.

## Usage

The package has the following command line arguments:
```
usage: protocol_qc [--min_match_score MIN_MATCH_SCORE] [--find_first] [--logs_dir LOGS_DIR]
                   [--sub_label SUB_LABEL] [--which_tags {none,highest,all}]
                   [--debug_level {INFO,DEBUG}] [-v] [-h] template acquisitions

protocol_qc: a simple package to ensure an MRI protocol was adhered to by comparing DICOM
             data to one or more user defined templates.

positional arguments:
  template              A json file containing the protocol template, or a folder containing
                        multiple protocol templates. If that later is provided, all protocol
                        templates in the folder will be compared to the data.
  acquisitions          A path to the root directory containing the DICOM series which are to
                        be compared against the protocol templates.

optional:
  --min_match_score MIN_MATCH_SCORE
                        Fractional match value used to consider matches for series and
                        protocols. At the series level, anything match score below this value
                        will not be considered (even for a partial match). At the protocol
                        level, matches below this value will not be included in the summary
                        of protocol matches.  (default: 0.8)
  --find_first          If providing multiple protocol templates, stop when a perfect
                        protocol match is found.  (default: False)
  --logs_dir LOGS_DIR   Directory for the logs will be written to. If the directory does not
                        exist, it will be created. If not provided, the logs will be written
                        into the current working directory.  (default: None)
 --sub_label SUB_LABEL
                        When generating a tags file, use this to specify a custom
                        subject_label. Not strictly necessary, as the contents of the
                        PatientID field will also be included in subject_details portion of
                        the tags file.  (default: None)
  --which_tags {none,highest,all}
                        Specifies in which situations the tags files should be generated.
                        'all' will generate a tag file per protocol template, 'highest' will
                        generate a tag file for only the highest (one or more) matches, while
                        'none' will turn of the tag generation feature all together.
                        (default: highest)

information arguments:
  --debug_level {INFO,DEBUG}
                        Level of logging when running. Select 'DEBUG' to have the logs list
                        each mismatched DICOM header field. (default: INFO)
  -v, --version         Version
  -h, --help            Show this help message and exit.

example: protocol_qc my_protocol_template.json directory_of_dicoms/
```

### Installation

To install a specific tag, switch to the (`<TAG>`):

```$ git checkout tags/<TAG>```

and then run:

```$ python3 -m pip install .```

It is recommended to install the package within a [virtual environment](https://docs.python.org/3/library/venv.html)
to avoid potential packaging conflicts.

### Limitations
- No check is performed to ensure there is a one-to-one mapping between the *series* template matches and the data.
- Only designed to work with Siemens scanners
- No ability to interrogate DICOM header data in the CSA
- Limited number of private tags available to check
- The first slice that is read in for classic DICOMS or the first "FunctionalGroupsSequence" for enhanced DICOMS is used to determine the DICOM metadata

### Contributing

Contributions are very welcome!
Please see [here](/CONTRIBUTING.md) for an overview on reporting issues and contributing to the code base.
