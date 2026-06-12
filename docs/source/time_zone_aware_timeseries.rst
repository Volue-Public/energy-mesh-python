===========================
Time zone-aware time series
===========================

Please refer to `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/time-series/time-zone-aware-time-series/>`_
for a general description of time zone-aware time series in Mesh.

The Mesh Python SDK allows for setting time zones
through its time series creation and update APIs:

:py:meth:`volue.mesh.Connection.Session.create_physical_timeseries`
:py:meth:`volue.mesh.Connection.Session.update_timeseries_resource_info`

For example:

.. code-block:: python

    result = session.create_physical_timeseries(
        path="/Path/To/Test/Timeseries/",
        name="Test_Timeseries",
        curve_type=Timeseries.Curve.PIECEWISELINEAR,
        resolution=Timeseries.Resolution.DAY,
        unit_of_measurement="cm",
        # time_zone is valid only if resolution is DAY or coarser
        time_zone="Europe/Warsaw"
    )
    session.commit()


See also the following examples:

* :ref:`examples:Create physical time series`
* :ref:`examples:Write time series`
* :ref:`examples:Time zone-aware time series conversion`


Transforming time zone-aware time series
========================================

When transforming a time zone-aware time series using
:py:meth:`volue.mesh.calc.transform.TransformFunctions.transform`, the
``timezone`` argument must be set to ``None``.

.. code-block:: python

    result = session.read_timeseries_points(
        target=ts_attribute,
        start_time=start,
        end_time=end,
    ).transform(
        resolution=Timeseries.Resolution.HOUR,
        method=transform.Method.AVG,
        timezone=None
    )

.. note::
    Before version 1.17 the default value of ``timezone`` was ``UTC``.
    This meant that to correctly transform a time zone-aware time series, the
    ``timezone`` argument had to be explicitly set to ``None``.
    Starting from version 1.17 the default is ``None``, so the argument can
    be omitted.
