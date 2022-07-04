======================
Rating curves
======================

A **rating curve** is used to convert water level in river measurements `x` in
a watercourse to discharge. In Mesh we use the following formula: 

.. math::
   f(x) = a * (x + b)^c

to approximate discharge, and we store rating curves as a set of segments where
each segment contains values for the 64 bit floating point factors `a`, `b`,
and `c`. Additionally each segment `i` stores a 64 bit floating point
`x_range_until` value and is valid for a range of `x` values
`[x_range_until[i-1], x_range_until[i])`.

For example, with a segment...

+---------------+-------+-------+-------+
| x_range_until | a     | b     | c     |
+===============+=======+=======+=======+
| 10            | 1.24  | 13.7  | 11.1  |
+---------------+-------+-------+-------+
| 50            | 11.2  | 1.0   | 6.65  |
+---------------+-------+-------+-------+
| 100           | 4.27  | 1.55  | 0.87  |
+---------------+-------+-------+-------+

...we'd have the following rating curve function:

.. math::
   f(x) =
   \begin{cases}
      1.24 * (x + 13.7)^{11.1} & \text{if } 0 \leq x \lt 10\\
      11.2 * (x + 1.0)^{6.65} & \text{if } 10 \leq x \lt 50\\
      4.27 * (x + 1.55)^{0.87} & \text{if } 50 \leq x \lt 100\\
      \text{nan} & \text{otherwise}
   \end{cases}

Rating curves can change over time because of for example changes in a river
due to erosion and sedimentation. Such changes affect the discharge function
and the function equation factors need to be adjusted. To reflect that the
rating curve segments in Mesh are grouped into **rating curve versions**. Each
version is timestamped with the time at which the version becomes active, and
the version is active until the next version, if any, becomes active.

+---------+---------------+-------+-------+-------+
| version | x_range_until | a     | b     | c     |
+=========+===============+=======+=======+=======+
| 2019    | 10            | 1.24  | 13.7  | 11.1  |
|         +---------------+-------+-------+-------+
|         | 50            | 11.2  | 1.0   | 6.65  |
|         +---------------+-------+-------+-------+
|         | 100           | 4.27  | 1.55  | 0.87  |
+---------+---------------+-------+-------+-------+
| 2020    | 10            | 3.31  | 11.7  | 12.1  |
|         +---------------+-------+-------+-------+
|         | 50            | 10.1  | 1.5   | 5.45  |
|         +---------------+-------+-------+-------+
|         | 100           | 5.00  | 1.32  | 0.96  |
+---------+---------------+-------+-------+-------+
| 2021    | 10            | 2.22  | 12.7  | 10.1  |
|         +---------------+-------+-------+-------+
|         | 50            | 11.1  | 1.3   | 5.65  |
|         +---------------+-------+-------+-------+
|         | 100           | 3.27  | 2.55  | 0.37  |
+---------+---------------+-------+-------+-------+

In addition each version has an `x_range_from` field, with the minimal `x` value
for the curve. For `x < x_range_from` for the given version the `f(x) = nan`.

In Mesh **rating curve attributes** contain a set of rating curve versions.
