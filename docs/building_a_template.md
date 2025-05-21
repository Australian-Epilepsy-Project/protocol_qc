# Building a template

## An introduction

The protocol template must be written in JSON, where the primary keys are the *acquisition labels*,
as well as a *GENERAL* key allocated for protocol wide settings and *fields*.

Within each *acquisition*, a *series* dictionary must be defined,
specifying all DICOM series that should be logically grouped together in an *acquisition*. 
For example, the magnitude and phase components of a scan would be grouped into an *acquisition* definition,
as would any additional series that had some sort of preprocessing performed (e.g., prescan normalise).
*Series* within an *acquisition* are expected to have sequential `SeriesNumber`s.

Each *series* should define a *fields* dictionary containing the DICOM header fields that are to be checked,
along with the method to check each field (see [Fields](#fields)).

If one wants to add custom to tags to the tags file, this can be specified in *tags* in the *GENERAL* section.
See [Custom Tags](#custom-tags).


Schematically, a template has the following structure:
```json
{
    "GENERAL": {
      "fields": {
        ....
      }
      ....
    },
    "acquisition_1": {
        "fields": {
          ....
        },
        "series": {
          "series_1": {
            "fields": {
              ....
            },
            ....
          },
          ...
          "series_n": {
            ....
          }
        }
    },
    ....
    "acquisition_n": {
        ....
    }
}
```

### Fields

*fields* dictionaries contain key-value pairs defining DICOM header fields that are to be checked,
along with the method to check each field.
The key is the name of the DICOM header field, as specified by [pydicom](https://pydicom.github.io/pydicom/stable/index.html),
the corresponding value is a dictionary containing two keys. "value" stores the value to check against,
along with the method of comparison stored in the "comparison" value.

There are four types of comparison operators available:
- `exact`
- `regex`
- `in_range`
- `in_set`

Note, if a regex comparison is performed on a list,
for example ImageType, and the template list is shorter than the list extracted from the DICOM header,
only the cells in the DICOM header list up to the range of the template list will be compared.

An example of a *fields* dictionary:
```json
"fields": {
  "SeriesDescription": {
    "value": "t1w",
    "comparison": "regex"
  },
  "SequenceName": {
    "value": "*tfl3d1_16ns",
    "comparison": "exact"
  }
}
```

*fields* can be defined at any level of the template,
and will be inherited by all template definitions lower in the hierarchy,
unless the "share_fields" flag has been set (see [Special Keys](#special-keys)).

**Accessing private fields**

Often important information is stored in so-called *private* tags in the DICOM header (https://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.8.html).
Currently a very limited number of these tags are available and differ between classic and enhanced DICOMS.

For classic DICOMS the folllowing are available using the following keys:
- `PRIVATE-Orientation` = `0x0051,0x100e`
- `PRIVATE-NumberOfImagesInMosaic` = `0x0019,0x100a`
- `PRIVATE-AcquisitionDuration` = `0x0051,0x100a`

For enhacned DICOMS the following are available (represented using `pydicom` notation):
- `ImageTypeText` = ['PerFunctionalGroupsSequence'][0][0x0021,0x11FE][0][0x0021,0x1175]

### Special keys

There are number of reserved special keys which control how the template is checked.
Some of these keys can be used at any level in the template, while others are level specific.
The following table summarises these keys.

|         Key            | Value        | Required | Default |
|------------------------|--------------|----------|---------|
| **Protocol Level**                                         |
| *allow_extra*          | bool         | no       | False   |
| *date_restriction*     | Dict         | no       | None    |
| *check_ordering*       | bool         | no       | False   |
| *tags*                 | Dict         | no       | None    |
| **Acquisition Level**                                      |
| *duplicates_allowed*   | bool         | no       | False   |
| *duplicates_expected*  | int          | no       | 0       |
| *paired_fmaps*         | Dict         | no       | None    |
| *share_fields*         | bool         | no       | True    |
| *is_optional*          | bool         | no       | False   |
| *ignore_ordering*      | bool         | no       | False   |
| *series*               | dict         | yes      | -       |
| **Series Level**                                           |
| *num_files*            | int          | no       | None    |
| *share_fields*         | bool         | no       | True    |

- *allow_extra*: If true, the presence of additional (unmatched) series will not be treated as an issue with the data.
- *date_restriction*: Either a single date indicating the start date of a protocol, or a dictionary containing one or both of the keys "start" and "end". 
- *check_ordering*: Check if the protocol adheres to the ordering specified in the template.
- *duplicates_allowed*: Set to true if the presence of duplicates for a given acquisition should not raise an error.
- *duplicates_expected*: If duplicate acquisitions are expected, this value can be set to an integer and will result in an error in protocol matching if the number of found duplicates does not match the template.
- *paired_fmaps*: Dictionary to describe if and how fmaps are expected to be paired with the acquisition. See [Paired field maps](#Paired-fieldi-maps) for more details.
- *ignore_ordering*: Exclude an *acquistion* from the final protocol ordering check.
- *is_optional*: Use to indicate if an acquisition need not be included in the data.
- *num_files*: Use to determine if the complete data was sent by specifying the number of expected DICOM files per series. See [Data completeness](#data-completeness) for more details on this topic.


#### Data Completeness

There are number of ways to ensure the complete data set for each series was sent, however the approach varies
depending on the type of data (classic, enhanced, MOSAIC etc).

For classic DICOM data with one slice per file, specifying the number of slices is sufficient.\
For data stored in MOSAIC format, the number of slices in conjunction with the series level *field* entry "NumberofImagesInMosaic" can be utilised.\
When checking enhanced DICOMS, the "NumberOfFrames" *field* should be used.

#### Duplicate acquisitions

There are scenarios in which an *acquisition* is acquired more than once.\
For this, the following fields are available:
- "duplicates_allowed" specifies whether any duplicates at all are allowed
- "duplicates_expected" can be set to the number of expected duplicates

Note: setting "duplicates_expected" to 0 (the default value) with "duplicates_allowed" to true means any number of duplicates are accepted.

#### Paired field maps

Sometimes *acquisitions* will have a corresponding field map (*fmap*) `acquisition` that is expected to be acquired sequentially with another corresponding *acquisition*. 
And often, there may be multiple *fmap* acquisitions recorded with identical settings, preventing them from being simply outlined in the protocol template as another *acquisition*. 
The *acquisition* field "paired_fmaps"  allows one to specify which *fmap* should be paired to the acquisition, as well as where it should be found relative to the acquisition.
One can specify "before", "after", or "both" when declaring the expected paired fmaps, and when defining the *fmaps*
themselves, the flag *ignore_ordering* should be set to true.

For example, an acquisition expecting a pair of *fmap* acquisitions after it would have the following in its definition:
```json
  "paired_fmaps" : {
    "which_acquisitions" : [
      "FMap",
      "Fmap_InvROPE"
    ],
    "position" : "after"
  }
```

## Example template

An [example protocol template](/docs/example_template.json) containing the following *acquisition* templates:
- a T1w *acquisition* (magnitude and phase *series*)
- diffusion sequence *acquisition* (Physio logs, single-band reference, magnitude and phase *series*)
- a functional MRI *acquisition* (magnitude, and phase *series*)
- a field map *acquisition* expected to be paired with the fMRI *acquisition*

## Tags

For each protocol template, a corresponding json file containing "tags" can be produced. The generation of the tags
file is controlled via the CLI argument `which_tags`, which accepts the options {`none`, `highest`, `all`}.

The produced tags files will contain matching scores for the following:
- protocol level (matched acquisitions / total acquisitions in protocol)
- acquisition level (matched series / total series in acquisition)
- series level (matched DICOM header fields / total DICOM header fields defined for series)

as well as a number of fields containing *protocol* wide level information. (See below for an example).

### Custom Tags

In addition to the default protocol matching tags that can be generated for each protocol template,
one can specify additional custom tags, which can be set based on some user defined criteria.

There are three methods to apply custom tags:
- `constant`: the tag is constant and applied without any criteria checks
- `fill_with`: the tag will be generated from the specified DICOM header field
- `options`: the tag depends on which "option" was satisfied. The specified options include the DICOM header\
field to check, the value to check it against, as well as the comparison method.

In the following example, the *tags* section of a protocol template is shown.
The `protocol_version` and `scanner_type` tags use the `constant` method and therefore will always be generated,
and have the values `v42` and `Apeture Science`, respectively.
The tag `scanner_software` uses the `fill_with` method, and will be extracted from the DICOM header field `SoftwareVersions`.
If it does not exist, "NOT FOUND" will be set.
Finally, the tag `site` uses the `options` method.
In this case, the DICOM header field `InsitutationName` is being checked, with the options for the tag being `Earth`, `Mars` and `Pluto`.

```json
{
  "GENERAL": {
    "tags": {
      "protocol_version": {
      "type": "constant",
      "tag": "v42"
      },
      "scanner_type": {
        "type": "constant",
        "tag": "Apeture Science"
      },
      "scanner_software": {
        "type": "fill_with",
        "tag": "SoftwareVersions"
      },
      "site": {
        "type": "options",
        "tag": {
          "Earth": {
            "field": "InstitutionName",
            "value": "Earth Base",
            "comparison": "exact"
          },
          "Mars": {
            "field": "InstitutionName",
            "value": ["Mars", "The Red Institute"],
            "comparison": "in_set"
          },
          "Pluto": {
            "field": "InstitutionName",
            "value": "Pluto MRI Services",
            "comparison": "regex"
          }
        }
      }
    }
  }
}
```

#### Example tags file

```json
{
  "software": {
    "generated_with": "protocol_assurance",
    "version": "0.1.0",
    "date": "2024-10-31"
  },
  "subject_details": {
    "custom_label": "101101",
    "patientID": "010010"
  },
  "custom_tags": {
    "protocol_version": "v42",
    "scanner": "Apeture Science",
    "scanner_software": "GLaDOS",
    "site": "Earth"
  },
  "protocol": {
    "template_name": "v42_apeture_scanners.json",
    "protocol_match_score": 1.0,
    "has_issue": false,
    "correct_ordering": "yes",
    "missing_data": false,
    "duplicates_allowed": false,
    "extra_series": {
      "allowed": false,
      "extra_series": 0
    },
    "acquisitions": {
      "T1w": {
        "duplicates_allowed": false,
        "duplicates_expected": 0,
        "duplicates_found": 0,
        "acquisitions": [
          {
            "acquisition_match_score": 1.0,
            "series": {
              "mag": {
                "series_match_score": 1.0,
                "matched": "1:T1w_Sag_AP-",
                "data_complete": true
              },
              "mag_prenorm": {
                "series_match_score": 1.0,
                "matched": "2:T1w_Sag_AP-",
                "data_complete": true
              }
            }
          }
        ]
      },
      ....,
      ....,
      "FLAIR": {
        "duplicates_allowed": false,
        "duplicates_expected": 0,
        "duplicates_found": 0,
        "acquisitions": [
          {
            "acquisition_match_score": 1.0,
            "series": {
              "mag_prenorm": {
                "series_match_score": 1.0,
                "matched": "41:T2wFLAIR_Sag_AP-_ORIG",
                "data_complete": true
              },
              "mag_prenorm_fill": {
                "series_match_score": 1.0,
                "matched": "42:T2wFLAIR_Sag_AP-",
                "data_complete": true
              }
            }
          }
        ]
      }
    }
  }
}
```
