# ProtocolQC by The Florey: Tutorial

The ProtocolQC tool is intended to act as the first line of defense
against undesirable or impermissible deviations from a planned image acquisition protocol.
The purpose of this tutorial is to demonstrate:
-   How to build an initial template that defines your expected acquisition protocol
    and the range of permissible deviations within such.
-   How to execute the tool to test for deviations of an acquired session from the template protocol.
-   How to *refine* the template to perform more exhaustive testing
    that may be necessary to catch certain issues.

This tutorial is spread across multiple markdown files:

-   [`00_datalad.md`](00_datalad.md):
    Introduces the DataLad software,
    and provides instructions on how to access the tutorial data.

-   [`01_firsttemplate.md`](01_firsttemplate.md):
    Demonstrates how to build from scratch
    a first working prototype of a protocol template,
    producing file [`templates/01_byseriesdescription.json`](templates/01_byseriesdescription.json).

-   [`02_seriesdescription.md`](02_seriesdescription.md):
    Shows why it is preferable to not base the protocol matching
    simply on the names of sequences,
    and how to instead base the matching
    on more intrinsic attributes of the sequences,
    producing file [`templates/02_bymetadata.json`](templates/02_bymetadata.json).

-   [`03_checkparams.md`](03_checkparams.md):
    Demonstrates how to expand the set of tests
    to check for potential unintended and/or undesirable changes
    to the parameters with which individual sequences are run
    that could be deleterious to the utility of the acquired data,
    producing file [`templates/03_checkparams.json`](templates/03_checkparams.json).

-   [`04_additional.md`](04_additional.md):
    Introduces a range of additional checks
    over and above the parameters of individual sequences,
    aggregating those changes into file
    [`templates/04_additional.json`](templates/04_additional.json).
