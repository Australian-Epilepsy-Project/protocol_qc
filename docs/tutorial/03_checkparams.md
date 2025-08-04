## Template 3: Checking sequence parameters

When checking for conformity of an imaging session against the intended protocol,
it may not be adequate to simply check that all of the expected image series are present.
It would be preferable to additionally check as many metadata fields as possible
in order to detect even minor unwanted deviations from the protocol plan.
In the third version of the protocol template,
checks for myriad sequence parameters are introduced.

### Session-specific metadata

Intuitively, if there are any metadata fields that are specific to an individual session,
then enforcing consistency of those fields between input data and the template
will yield a mismatch,
even if the imaging session entirely conformed to the planned protocol.
It is up to the individual user to discern which metadata fields
should be checked against the template.
So for instance,
adding the date and time of acquisition to the template would not be sensible.

### Examples from revised protocol template

#### Metadata applicable to the whole session

At the head of new protocol template [`templates/03_checkparams.md`](templates/03_checkparams.json),
the following was added:

```json
{
  "GENERAL": {
    "fields": {
      "BodyPartExamined": {
        "value": "BRAIN",
        "comparison": "exact",
        "compulsory": false
      },
      "AngioFlag": {
        "value": "N",
        "comparison": "exact",
        "compulsory": false
      },
      "ImagedNucleus": {
        "value": "1H",
        "comparison": "exact",
        "compulsory": false
      },
      "MagneticFieldStrength": {
        "value": 3,
        "comparison": "exact",
        "compulsory": false
      },
      "TransmitCoilName": {
        "value": "Body",
        "comparison": "exact",
        "compulsory": false
      },
      "dBdt": {
        "value": 0,
        "comparison": "exact",
        "compulsory": false
      },
      "PatientPosition": {
        "value": "HFS",
        "comparison": "exact",
        "compulsory": false
      }
    }
  },
  ...
```

Conformity to these metadata fields is enforced for all acquisitions
and therefore all series.
One distinction here is that for each of these fields,
an additional flag has been added that specifies that it is *not compulsory*
for these fields to appear in the empirical metadata;
that is, if that field is absent from the input data,
that is *not* considered a mismatch against the template;
it is only when that field is present,
but has a value different to that of the template,
that the data are considered to not match the template.
Use of this field is necessary for these session-level parameters
as there are some scanner-generated derivative image series that omit these fields.

#### Exemplar sequence

Here we utilise the same T2*-weighted multi-echo gradient echo sequence
as was presented as an example
in previous document [`02_seriesdescription.md`](02_seriesdescription.md).

Here is the relevant template for that acquisition
within version 2 of the session template [`templates/02_bymetadata.json`](templates/02_bymetadata.json):

```json
  ...
  },
  "T2*-weighted multi-echo gradient echo": {
    "fields": {
      "Modality": {
        "value": "MR",
        "comparison": "exact"
      },
      "ScanningSequence": {
        "value": "GR",
        "comparison": "exact"
      },
      "SequenceVariant": {
        "value": [
          "SP",
          "OSP"
        ],
        "comparison": "exact"
      },
      "ScanOptions": {
        "value": "",
        "comparison": "exact"
      },
      "MRAcquisitionType": {
        "value": "3D",
        "comparison": "exact"
      },
      "SequenceName": {
        "value": "^\\*fl3d\\d+r",
        "comparison": "regex"
      }
    },
    "series": {
      "Magnitude (original)": {
        "fields": {
          "ImageType": {
            "value": [
              "ORIGINAL",
              "PRIMARY",
              "M",
              "ND"
            ],
            "comparison": "exact"
          }
        }
      },
      "Magnitude (normalised)": {
        "fields": {
          "ImageType": {
            "value": [
              "ORIGINAL",
              "PRIMARY",
              "M",
              "ND",
              "NORM"
            ],
            "comparison": "exact"
          }
        }
      },
      "Phase": {
        "fields": {
          "ImageType": {
            "value": [
              "ORIGINAL",
              "PRIMARY",
              "P",
              "ND"
            ],
            "comparison": "exact"
          }
        }
      },
      "R2* map": {
        "fields": {
          "ImageType": {
            "value": [
              "DERIVED",
              "PRIMARY",
              "R2_STAR MAP",
              "ND",
              "NORM"
            ],
            "comparison": "exact"
          }
        }
      }
    }
  },
  ...
```

And here is the corresponding section
in the new version of that acquisition template
[`templates/03_checkparams.json`](templates/03_checkparams.json):

```json
  ...
  },
  "T2*-weighted multi-echo gradient echo": {
    "fields": {
      "Modality": {
        "value": "MR",
        "comparison": "exact"
      },
      "ScanningSequence": {
        "value": "GR",
        "comparison": "exact"
      },
      "SequenceVariant": {
        "value": [
          "SP",
          "OSP"
        ],
        "comparison": "exact"
      },
      "ScanOptions": {
        "value": "",
        "comparison": "exact"
      },
      "MRAcquisitionType": {
        "value": "3D",
        "comparison": "exact"
      },
      "SequenceName": {
        "value": "^\\*fl3d\\d+r",
        "comparison": "regex"
      },
      "SliceThickness": {
        "value": 5,
        "comparison": "exact"
      },
      "RepetitionTime": {
        "value": 25,
        "comparison": "exact"
      },
      "EchoTime": {
        "value": [
          10,
          15,
          20
        ],
        "comparison": "in_set"
      },
      "NumberOfAverages": {
        "value": 1,
        "comparison": "exact"
      },
      "EchoNumbers": {
        "value": [
          1,
          2,
          3
        ],
        "comparison": "in_set"
      },
      "NumberOfPhaseEncodingSteps": {
        "value": 63,
        "comparison": "exact"
      },
      "EchoTrainLength": {
        "value": 3,
        "comparison": "exact"
      },
      "PercentSampling": {
        "value": 100,
        "comparison": "exact"
      },
      "PercentPhaseFieldOfView": {
        "value": 90.625,
        "comparison": "exact"
      },
      "PixelBandwidth": {
        "value": 310,
        "comparison": "exact"
      },
      "AcquisitionMatrix": {
        "value": [
          64,
          0,
          0,
          58
        ],
        "comparison": "exact"
      },
      "InPlanePhaseEncodingDirection": {
        "value": "COL",
        "comparison": "exact"
      },
      "FlipAngle": {
        "value": 15,
        "comparison": "exact"
      },
      "VariableFlipAngleFlag": {
        "value": "N",
        "comparison": "exact"
      },
      "Rows": {
        "value": 58,
        "comparison": "exact"
      },
      "Columns": {
        "value": 64,
        "comparison": "exact"
      },
      "PixelSpacing": {
        "value": [
          3.59375,
          3.59375
        ],
        "comparison": "exact"
      },
      "PRIVATE-Orientation": {
        "value": "^(Cor|C>.*)$",
        "comparison": "regex"
      },
      "PRIVATE-GradientMode": {
        "value": "Normal",
        "comparison": "exact"
      },
      "PRIVATE-ParallelImagingAcceleration": {
        "value": "p3",
        "comparison": "exact"
      }
    },
    "series": {
      "Magnitude (original)": {
        "fields": {
          "ImageType": {
            "value": [
              "ORIGINAL",
              "PRIMARY",
              "M",
              "ND"
            ],
            "comparison": "exact"
          }
        }
      },
      "Magnitude (normalised)": {
        "fields": {
          "ImageType": {
            "value": [
              "ORIGINAL",
              "PRIMARY",
              "M",
              "ND",
              "NORM"
            ],
            "comparison": "exact"
          }
        }
      },
      "Phase": {
        "fields": {
          "ImageType": {
            "value": [
              "ORIGINAL",
              "PRIMARY",
              "P",
              "ND"
            ],
            "comparison": "exact"
          }
        }
      },
      "R2* map": {
        "fields": {
          "ImageType": {
            "value": [
              "DERIVED",
              "PRIMARY",
              "R2_STAR MAP",
              "ND",
              "NORM"
            ],
            "comparison": "exact"
          }
        }
      }
    }
  },
  ...
```

There are many more sequence parameters that are now being checked
for conformity against the template.
File [`templates/03_checkparams.json`](templates/03_checkparams.json)
introduces checks for a vast array of sequence parameters
across most of the acquisitions within the session protocol.

The tutorial sample data
additionally includes a range of sessions
where individual sequence parameters have been altered
with respect to the template protocol;
the efficiacy with which the ProtocolQC software detects these deviations
is explored in:
[Individual sequence parameter discordances](sessions/README.md#individual-sequence-parameter-discordances).

In the next tutorial documentation page [`04_additional.md`](04_additional.md),
it is shown how to introduce additional checks into the protocol template
over and above these per-sequence parameters.
