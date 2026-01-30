"""
Functionality for working with time series resources.
"""

from __future__ import annotations

from dataclasses import dataclass

from volue.mesh import Timeseries
from volue.mesh._common import _from_proto_curve_type, _from_proto_resolution
from volue.mesh.proto.time_series.v1alpha import time_series_pb2


def _get_unit_of_measurement(
    proto_timeseries_resource: time_series_pb2.TimeseriesResource,
):
    if proto_timeseries_resource.HasField("unit_of_measurement"):
        return proto_timeseries_resource.unit_of_measurement.name
    return None


@dataclass
class TimeseriesResource:
    """Represents a Mesh time series resource (either physical or virtual)."""

    timeseries_key: int
    path: str
    name: str
    temporary: bool
    curve_type: Timeseries.Curve
    resolution: Timeseries.Resolution
    unit_of_measurement: str | None
    virtual_timeseries_expression: str | None = None
    time_zone: str | None = None

    @classmethod
    def _from_proto_timeseries_resource(
        cls, proto_timeseries_resource: time_series_pb2.TimeseriesResource
    ) -> TimeseriesResource:
        """Create a `TimeseriesResource` from protobuf TimeseriesResource.

        Args:
            proto_timeseries_resource: Protobuf TimeseriesResource returned from the gRPC methods.
        """
        resource = cls(
            timeseries_key=proto_timeseries_resource.timeseries_key,
            path=proto_timeseries_resource.path,
            name=proto_timeseries_resource.name,
            temporary=proto_timeseries_resource.temporary,
            curve_type=_from_proto_curve_type(proto_timeseries_resource.curve_type),
            resolution=_from_proto_resolution(proto_timeseries_resource.resolution),
            unit_of_measurement=_get_unit_of_measurement(proto_timeseries_resource),
            virtual_timeseries_expression=proto_timeseries_resource.virtual_timeseries_expression,
            time_zone=proto_timeseries_resource.time_zone if proto_timeseries_resource.time_zone else None,
        )

        return resource
