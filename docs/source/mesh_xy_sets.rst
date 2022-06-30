XY-sets in Mesh
===============

An XY-set is a set of two-dimensional curves. Mesh supports storing XY-sets in
XY-set XY-set attributes, which can be versioned or unversioned. This document
will explain what XY-curves and XY-sets are, how Mesh XY-set attributes are
structured, and how you can use the Mesh Python SDK to access the XY-sets in
those attributes.


XY-curves
---------

An **XY curve** is a set of `(x, y)` pairs where `x` and `y` are 64 bit
floating point values.

+--------+-----------+
|      x |         y |
+========+===========+
|      1 |         2 |
+--------+-----------+
|      2 |       1.5 |
+--------+-----------+
|      3 |       0.5 |
+--------+-----------+
|     10 |        -1 |
+--------+-----------+


XY-sets
-------

An **XY set** is a set of XY curves, each curve indexed by a 64 bit floating
point reference value. These reference values are sometimes called Z. We often
visualize **XY sets** like so:

+-----+---------+---------+
| | x |  | z    |  | z    |
|     |  | y    |  | y    |
+=====+=========+=========+
|     |   **0** | **180** |
+-----+---------+---------+
|     |     1.5 |     0.3 |
+-----+---------+---------+
|   3 |     0.5 |       1 |
+-----+---------+---------+
|  10 |      -1 |       9 |
+-----+---------+---------+

- The first non-header row contains the reference/Z values for that column.
- Usually the headers will have actual names, see further below.

A **versioned XY set** is a versioned list of XY sets. Each XY set in the list
has a timestamp which indicates the start of the active period for that XY set,
and the XY set is active until the next time-sorted XY set in the versioned XY
set becomes active.

Mesh has attribute types for **XY sets** (:code:`XYSetAttribute`) and
**versioned XY sets** (:code:`XYZSeriesAttribute`). In the attribute definitions
of those attributes we store a description and a unit of measurement for each of
X, Y, and Z. For example if we have the following axis definitions...

+------+----------------+---------------------+
| Axis | Description    | Unit of measurement |
+======+================+=====================+
| X    | Wind speed     | m/s                 |
+------+----------------+---------------------+
| Y    | Production     | MW                  |
+------+----------------+---------------------+
| Z    | Wind direction | degrees             |
+------+----------------+---------------------+

...Nimbus will visualize the above XY set as:

+--------------------+----------------------------+----------------------------+
| | Wind speed [m/s] | | Wind direction [degrees] | | Wind direction [degrees] |
|                    | | Production [MW]          | | Production [MW]          |
+====================+============================+============================+
|                    |                      **0** |                    **180** |
+--------------------+----------------------------+----------------------------+
|                  2 |                        1.5 |                        0.3 |
+--------------------+----------------------------+----------------------------+
|                  3 |                        0.5 |                          1 |
+--------------------+----------------------------+----------------------------+
|                 10 |                         -1 |                          9 |
+--------------------+----------------------------+----------------------------+
