## Exemplar sessions

This document provides a list of individual sessions
against which the ProtocolQC software can be checked
to demonstrate the effects of specific protocol non-conformities.
The data for each of these individual sessions
are [made available through DataLad](../00_datalad.md).

### Individual sequence parameter discordances

-   [Session `101`](101.md):
    Disabled RF spoiling on dual-echo gradient echo field mapping sequence.

-   [Session `102`](102.md):
    K-space zero-padding ("interpolation") activated on T1-weighted FLASH sequence.

-   [Session `103`](103.md):
    K-space filtering "raw filter" activated on T2-weighted Turbo Spin Echo sequence.

    (*Note*: Not detected)

-   [Session `104`](104.md):
    Change to slice encoding direction.

-   [Session `105`](105.md):
    Change to elliptical scanning.

    (*Note*: Not detected)

-   [Session `106`](106.md):
    Modification of phase oversampling.

-   [Session `107`](107.md):
    Modification to fat saturation.

    (*Note*: Not detected)

-   [Session `108`](108.md):
    Inclusion of gradient non-linearity distortion correction.

-   [Session `109`](109.md):
    Modification to phase partial Fourier.

-   [Session `110`](110.md):
    Change to gradient mode.

-   [Session `111`](111.md):
    Change to "distance factor" (spacing between 2D slices).

-   [Session `112`](112.md):
    Change to CMRR sequence special parameter "disable frequency update".

    (*Note*: Not detected)

More sessions to come.

### Higher-level protocol discordances

-   [Session `001`](001.md):
    Correctly identifies absence of discordance.

-   [Session `002`](002.md):
    Missing acquisition.

-   [Session `003`](003.md):
    Reordering of acquisitions that may be deemed inconsequential.

-   [Session `004`](004.md):
    Expected acquisition producing an unexpected image series.

-   [Session `005`](005.md):
    Reordering of acquisitions detrimental to protocol design.

-   [Session `006`](006.md):
    Unexpected acquisition duplication.

-   [Session `007`](007.md):
    Expected derivative image series missing from expected acquisition.

-   [Session `008`](008.md):
    Premature termination of sequence.

-   [Session `009`](009.md):
    Incomplete transfer of image data.

-   [Session `010`](010.md):
    Incorrect diffusion MRI gradient table.

-   [Session `011`](011.md):
    Failure to apply reversal of phase encoding.

-   [Session `012`](012.md):
    Erroneous double application of phase encoding reversal in CMRR EPI sequence.

-   [Session `013`](013.md):
    Unexpected and unrecognised acquisition.

-   [Session `014`](014.md):
    Incorrect fMRI task paradigm.

-   [Session `015`](015.md):
    Utilisation of wrong head coil.
