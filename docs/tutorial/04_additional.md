## Template 4: Higher-level protocol conformity

Version 3 of the template above is capable of detecting *many*,
but *not all*,
possible deviations from a planned protocol.
To explore the breadth of possible deviations
that this software tool would ideally be capable of detecting,
the template protocol has been repeatedly re-acquired
with a range of different intentional deviations from the planned protocol.
In this section,
we evaluate which of these deviations can be detected
using version 3 of the protocol template,
and how that template could possibly be modified
to catch as many of these issues as possible.

Within the `data/` directory,
there are many re-executions of the protocol,
acquiring repeated data on the phantom
with a range of variations introduced.
These are enumerated to obscure the nature of each;
it is the role of the ProtocolQC software
(and the designer of the protocol template)
to diagnose the deviations within these datasets.

Docuemntation page [`sessions/README.md`](sessions/README.md)
provides a list of these sessions,
linking to individual pages per sesions
that explain what the software reports in each instance,
how to interpret those results,
and the nature of the actual deviations
that were manually introduced into each of those sessions.
Many of these pages suggest changes to the template protocol,
which are applied using file [`templates/03_checkparams.json`](templates/03_checkparams.json)
generated in page [`03_checkparams.md`](03_checkparams.md)
as the basis,
aggregating those changes into file [`templates/04_additional.json`](templates/04_additional.json).
