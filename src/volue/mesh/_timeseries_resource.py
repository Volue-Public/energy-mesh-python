"""
Functionality for working with time series resources.
"""

from __future__ import annotations

from dataclasses import dataclass

from volue.mesh import Timeseries
from volue.mesh._common import _from_proto_curve_type, _from_proto_resolution
from volue.mesh.proto.core.v1alpha import core_pb2


@dataclass
class TimeseriesResource:
    """Represents a Mesh time series resource (either physical or virtual)."""

    timeseries_key: int = None
    path: str = None
    name: str = None
    temporary: bool = None
    curve_type: Timeseries.Curve = None
    resolution: Timeseries.Resolution = None
    unit_of_measurement: str = None
    virtual_timeseries_expression: str = None

    @classmethod
    def _from_proto_timeseries_resource(cls,
        proto_timeseries_resource: core_pb2.TimeseriesResource) -> TimeseriesResource:
        """Create a `TimeseriesResource` from protobuf TimeseriesResource.

        Args:
            proto_timeseries_resource: Protobuf TimeseriesResource returned from the gRPC methods.
        """
        resource = cls()
        resource.timeseries_key = proto_timeseries_resource.timeseries_key
        resource.path = proto_timeseries_resource.path
        resource.name = proto_timeseries_resource.name
        resource.temporary = proto_timeseries_resource.temporary
        resource.curve_type = _from_proto_curve_type(proto_timeseries_resource.curve_type)
        resource.resolution = _from_proto_resolution(proto_timeseries_resource.resolution)
        resource.unit_of_measurement = proto_timeseries_resource.unit_of_measurement
        resource.virtual_timeseries_expression = proto_timeseries_resource.virtual_timeseries_expression

        return resource
