==========================
Time zone-aware timeseries
==========================


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
        time_zone="Europe/Warsaw",
    )
    session.commit()


See also the following examples:

* :ref:`examples:Create physical time series`
* :ref:`examples:Write time series`
* :ref:`examples:Time zone-aware time series conversion`
