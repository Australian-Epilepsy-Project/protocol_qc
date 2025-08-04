## Sample data

This tutorial makes use of a collection of MRI sessions
where data were acquired on a phantom
with intentional deviations from a baseline template session.
These data are publicly available,
and are additionally configured as a *submodule* of this `git` repository.

### Downloading the data

Obtain these data can be done in multiple ways:

1.  (*recommended*) Utilising the `git submodule` capability.

    This both places the data in the appropriate location
    for the example commands provided in the tutorial to execute without modification,
    and ensures version matching between the tutorial documentation
    and the data to which it refers.

    From the root of a clone of the ProtocolQC software, run:

    ```sh
    git submodule init
    git submodule update
    ```

    The data should now be stored in location `docs/tutorial/data/`.

2.  Manually clone the data repository.

    The tutorial data can be obtained using eg.:

    ```sh
    git clone git@github.com:Australian-Epilepsy-Project/ProtocolDeviations.git
    ```

    Note however that invocations of the ProtocolQC software
    following the tutorial material
    may need to be altered to reflect the relative filesystem locations
    of these data vs. protocol templates.

3.  Download an archive of the data

    If one is not comfortable with `git`,
    you could instead download an unzip the data from:
    https://github.com/Australian-Epilepsy-Project/ProtocolDeviations/archive/refs/heads/main.zip

### Inspect the datasets

To see a list of all image acquisition sessions provided in the dataset:

```sh
ls data/
```

Each session consists of a PDF document "`protocol.pdf`",
which is generated at the scanner console and shows all sequences executed and their full parameter listings,
and a directory that contains a set of DICOM series.

To see the full filesystem tree of the template session:

```sh
tree data/Template/
```

Comparing this filesystem listing
to the first page of the corresponding PDF document `data/Template/protocol.pdf`,
it is hopefully clear that there is not perfect correspondence.
This is because for many MRI sequences,
a single execution of the sequence can yield multiple DICOM image series;
this could be magnitude and phase components of a complex image,
different variants of the image that have undergone different amounts of processing,
or generation of parametric maps by the scanner reconstruction.
