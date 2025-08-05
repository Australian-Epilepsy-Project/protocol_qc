# protocol_qc: A MRI protocol quality control tool

[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

## Overview

`protocol_qc` is a Python package that aims to allow one to validate a DICOM study
against a predefined template file containing key protocol parameters,
primarily via validation of DICOM header fields.
An overall matching score is calculated for each protocol template,
along with any additional information relating to missing/extra series,
as well as missing data (i.e., missing slices).

**Terminology**

The follow definitions are used by `protocol_qc`.
- *series*: One or more DICOMs with the same SeriesUID.
- *acquisitions*: One or more DICOM *series* that are logically grouped together
  due to all having been produced from a single execution of a given pulse sequence.
  E.g.:
    - Magnitude and phase components from a single scan.
    - For functional scans, both single-band reference and multi-band BOLD *series*.
- *protocol*: A planned set of *acquisitions* intended to be collected during a single scanning session.

Note: `protocol_qc` is very much still under development, and therefore one should be aware of its [limitations](#limitations).

## Usage

### Inputs

1.  One or more user-defined *template files* must be provided.
    For specification details see the template introduction [here](/docs/building_a_template.md).
2.  DICOM data from a *single imaging session*.

### Outputs

A collection of logs will be generated during the assessment process.
A summary log contains information about the DICOM data (number of series, slices etc),
as well as a brief summary of all protocol template matches.
Additionally, individual logs for each protocol template are generated and contain detailed information about the matching procedure.

Lastly, a json file containing basic information about the protocol matching can be generated for each template protocol.
This so-called "`tags`" file will be created in the same location as the logs.
The name of tags file will follow `<patient_identifier>_tags_<protocol_template_filename>.json`,
where `<patient_identifier>` can be set with the CLI argument `sub_label`,
otherwise it will default to the content in the DICOM header field 'PatientID'.
These files contain basic information such as the matching score, at the series, acquisition and protocol level,
as well as to which data series the template series were matched.
Additional `custom_tags` can be specified via the template. See [here](/docs/building_a_template.md) for more details.

### Full command-line usage

The package has the following command-line arguments:
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

## Installation

To install a specific version of the software,
ensure that that is the version of code being accessed:

```ShellSession
git checkout tags/<TAG>
```

(replacing string "`<TAG>`" with the version number of the software)

### Python native install

Run from the root directory of the repository:

```ShellSession
python3 -m pip install .
```

It is recommended to install the package within a [virtual environment](https://docs.python.org/3/library/venv.html)
to avoid potential packaging conflicts.

### `docker` container

Both building and executing `docker` containers
requires either that the user's account on their operating system
be a member of the "`docker`" *group*,
or have the permissions necessary to run the commands below using `sudo`.

To build the image locally, run from the repository root directory:

```ShellSession
docker build . -t aepflorey/protocol_qc:<TAG>
```

(replace "`<TAG>`" with the specific version of the software checked out,
or simply use the default `docker` tag of "`latest`")

Alternatively pull the image from DockerHub:

```ShellSession
docker pull aepflorey/protocol_qc:<TAG>
```

To run the container requires explicit *binding* of those paths on the host system
that the container needs to be able to read/write from.
In this example,
the host system has three sub-directories within the working directory:
-   "`DICOM/`" contains the input session to be analysed;
-   "`templates/`" contains one or more protocol templates against which the input data are to be checked;
-   "`logs/`" is a temporary directory in which to store log files that is created just before use.

Each of these directories is mounted relative to the root directory within the container.

```ShellSession
mkdir logs
docker run \
    -it \
    --rm \
    -v $(pwd)/DICOM:/input \
    -v $(pwd)/templates:/templates \
    -v ${pwd}/logs:/output \
    aepflorey/protocol_qc:latest \
    /templates \
    /input \
    --logs_dir /output
```

### Apptainer

Apptainer is an appealing alternative to `docker` for multiple reasons:
-   The image is a single file on the filesystem that can be distributed.
-   The image file can be run as though it is an executable.
-   No need for escalated privileges to run containers.
-   No need for explicit filesystem bindings.

To build an Apptainer image from the `docker` image
(note that this *building* step may require escalated privileges)

```ShellSession
# From a local Docker image
apptainer build ProtocolQC_<TAG>.sif docker-daemon://aepflorey/protocol_qc:<TAG>
# From DockerHub without installing the Docker image locally
apptainer build ProtocolQC_<TAG>.sif docker://aepflorey/protocol_qc:<TAG>
```

(as above, replacing "`<TAG>`" with the corresponding software version tag being built)

To then run the tool:

```ShellSession
mkdir logs
ProtocolQC_<TAG>.sif templates/ DICOM/ --logs_dir logs/
```

## Limitations

- No check is performed to ensure there is a one-to-one mapping between the *series* template matches and the data.
- Only designed to work with Siemens scanners.
- No ability to interrogate DICOM header data in the CSA.
- Limited number of private tags available to check.
- The first slice that is read in for classic DICOMS or the first "FunctionalGroupsSequence" for enhanced DICOMS is used to determine the DICOM metadata.

## Contributing

Contributions are very welcome!
Please see [here](/CONTRIBUTING.md) for an overview on reporting issues and contributing to the code base.
