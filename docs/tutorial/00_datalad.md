## Sample data

This tutorial makes use of a collection of MRI sessions
where data were acquired on a phantom
with intentional deviations from a baseline template session.
These data are most conveniently accessed using the DataLad command-line interface.
DataLad can be thought of as a version control system much like `git` for software code,
but intended for the distribution and usage of larger data.
Using this approach will therefore require that DataLad be installed in your operating environment.

### Installing the DataLad software

For instructions on the multiple avenues by which to install DataLad:
https://www.datalad.org/

### Clone the dataset

In the vernacular of version control systems such as `git` and DataLad,
to "clone" a repository is to take a snapshot of a dataset stored in some location
and create a duplicate elsewhere.
In addition to the duplication of data,
this will typically also involve some form of configuration of how certain commands
will communicate with the "origin" / "remote" instance of the repository that was cloned,
given that at any time following that clone
either one of the instances of that repository may be changed.
A key feature of DataLad however
is that when this initial "clone" operation is first performed,
it does *not* duplicate all of the data in that repository onto the local system.
Instead, it offers mechanisms by which to download large data files only when they are required.

```sh
datalad clone https://osf.io/dz5mc/ data/
```

### Inspect the dataset

To see a list of all image acquisition sessions provided in the dataset:

```sh
ls data/
```

Each session consists of a PDF document,
which is generated at the scanner console and shows all sequences executed and their full parameter listings,
and a directory that contains a set of DICOM series.

To see the full filesystem tree of the template session:

```sh
tree data/Template/
```

**TODO** Need to grab PDF for template;
currently only have it for the modified sessions

Comparing this filesystem listing to the first page of the corresponding PDF document,
it is hopefully clear that there is not perfect correspondence.
This is because for many MRI sequences,
a single execution of the sequence can yield multiple DICOM image series;
this could be magnitude and phase components of a complex image,
different variants of the image that have undergone different amounts of processing,
or generation of parametric maps by the scanner reconstruction.

It was previously mentioned
that DataLad will by default not actually download all data files wthin a dataset
at the point at which it is cloned.
The way this will appear on the file system
is that the file will be *presented*, but be of *zero size*.
See for instance the `.dcm` files containing the localiser data:

```sh
ls -la data/Template/1_localiser/
```

At the point at which you actually require the content of those data files,
it is necessary to make an explicit request to DataLad to acquire them.
This can be done for individual files,
or for all files within a directory.
Here it makes sense for us to acquire all of the image data
corresponding to the template session:

```sh
datalad get data/Template
ls -la data/Template/1_localiser/
```

These files now contain actual data.
