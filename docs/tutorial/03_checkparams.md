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
      "BodyPartExamined": { "exactly_if_present": "BRAIN" },
      "AngioFlag": { "exactly_if_present": "N" },
      "ImagedNucleus": { "exactly_if_present": "1H" },
      "MagneticFieldStrength": { "exactly_if_present": 3 },
      "TransmitCoilName": { "exactly_if_present": "Body" },
      "dBdt": { "exactly_if_present": 0 },
      "PatientPosition": { "exactly_if_present": "HFS" }
    }
  },
```

Conformity to these metadata fields is enforced for all acquisitions
and therefore all series.
One distinction here is that for each of these fields,
the name of the comparison `"exactly_if_present"` implies
that it is *not compulsory* for these fields to appear in the empirical metadata;
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
  },
  "T2*-weighted multi-echo gradient echo": {
    "fields": {
      "Modality": { "exactly": "MR" },
      "ScanningSequence": { "exactly": "GR" },
      "SequenceVariant": { "exactly": [ "SP", "OSP" ] },
      "ScanOptions": { "exactly": "" },
      "MRAcquisitionType": { "exactly": "3D" },
      "SequenceName": { "regex": "^\\*fl3d\\d+r" }
    },
    "series": {
      "Magnitude (original)": {
        "fields": {
          "ImageType": { "exactly": [ "ORIGINAL", "PRIMARY", "M", "ND" ] }
        }
      },
      "Magnitude (normalised)": {
        "fields": {
          "ImageType": { "exactly": [ "ORIGINAL", "PRIMARY", "M", "ND", "NORM" ] }
        }
      },
      "Phase": {
        "fields": {
          "ImageType": { "exactly": [ "ORIGINAL", "PRIMARY", "P", "ND" ] }
        }
      },
      "R2* map": {
        "fields": {
          "ImageType": { "exactly": [ "DERIVED", "PRIMARY", "R2_STAR MAP", "ND", "NORM" ] }
        }
      }
    }
  },
```

And here is the corresponding section
in the new version of that acquisition template
[`templates/03_checkparams.json`](templates/03_checkparams.json):

```json
  },
  "T2*-weighted multi-echo gradient echo": {
    "fields": {
      "Modality": { "exactly": "MR" },
      "ScanningSequence": { "exactly": "GR" },
      "SequenceVariant": { "exactly": [ "SP", "OSP" ] },
      "ScanOptions": { "exactly": "" },
      "MRAcquisitionType": { "exactly": "3D" },
      "SequenceName": { "regex": "^\\*fl3d\\d+r" },
      "SliceThickness": { "exactky": 5 },
      "RepetitionTime": { "exactly": 25 },
      "EchoTime": { "in_set": [ 10, 15, 20 ] },
      "NumberOfAverages": { "exactly": 1 },
      "EchoNumbers": { "in_set": [ 1, 2, 3 ] },
      "NumberOfPhaseEncodingSteps": { "exactly": 63 },
      "EchoTrainLength": { "exactly": 3 },
      "PercentSampling": { "exactly": 100 },
      "PercentPhaseFieldOfView": { "exactly": 90.625 },
      "PixelBandwidth": { "exactly": 310 },
      "AcquisitionMatrix": { "exactly": [ 64, 0, 0, 58 ] },
      "InPlanePhaseEncodingDirection": { "exactly": "COL" },
      "FlipAngle": { "exactly": 15 },
      "VariableFlipAngleFlag": { "exactly": "N" },
      "Rows": { "exactly": 58 },
      "Columns": { "exactly": 64 },
      "PixelSpacing": { "exactly": [ 3.59375, 3.59375 ] },
      "PRIVATE-Orientation": { "regex": "^(Cor|C>.*)$" },
      "PRIVATE-GradientMode": { "exactly": "Normal" },
      "PRIVATE-ParallelImagingAcceleration": { "exactly": "p3" }
    },
    "series": {
      "Magnitude (original)": {
        "fields": {
          "ImageType": { "exactly": [ "ORIGINAL", "PRIMARY", "M", "ND" ] }
        }
      },
      "Magnitude (normalised)": {
        "fields": {
          "ImageType": { "exactly": [ "ORIGINAL", "PRIMARY", "M", "ND", "NORM" ] }
        }
      },
      "Phase": {
        "fields": {
          "ImageType": { "exactly": [ "ORIGINAL", "PRIMARY", "P", "ND" ] }
        }
      },
      "R2* map": {
        "fields": {
          "ImageType": { "exactly": [ "DERIVED", "PRIMARY", "R2_STAR MAP", "ND", "NORM" ] }
        }
      }
    }
  },
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
