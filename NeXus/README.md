# About the NXxpcs (NeXus application definition)

`NXxpcs` describes the structure of a NeXus/HDF5 datafile used to
describe XPCS results computed by software external (to the [Bluesky
framework](https://blueskyproject.io/)) and to import those results into
Bluesky for visualization and other activities.

In this repository, we prepare the `NXxpcs` application _before_ we
submit it to the [NeXus definitions
repository](https://github.com/nexusformat/definitions) per the [NIAC
guidelines for
contributions](https://manual.nexusformat.org/classes/contributed_definitions/index.html).

It uses either or both of these two proposed base classes which
describe, in different ways, a mask or region of interest referencing
some portion of a ``NXdata`` group described by a mask array:

* `NXarraymask.nxdl.xml` : describe as collection of 2-D arrays
* `NXparameterizedmask.nxdl.xml` : describe as known model with parameters
