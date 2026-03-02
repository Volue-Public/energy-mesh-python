"""
Tests for volue.mesh._common.
"""

import sys
import uuid

import pytest

from volue.mesh import Timeseries, _common
from volue.mesh.proto.type import resources_pb2


@pytest.mark.unittest
@pytest.mark.parametrize(
    "timeseries",
    [
        Timeseries(full_name="full_name"),
        Timeseries(uuid_id=uuid.uuid4()),
        Timeseries(timskey=100),
        Timeseries(full_name="full_name", uuid_id=uuid.uuid4()),
        Timeseries(full_name="full_name", timskey=100),
        Timeseries(uuid_id=uuid.uuid4(), timskey=100),
        Timeseries(full_name="full_name", uuid_id=uuid.uuid4(), timskey=100),
    ],
)
def test_to_proto_mesh_id_from_timeseries(timeseries):
    mesh_id = _common._to_proto_mesh_id_from_timeseries(timeseries)
    if timeseries.full_name is not None:
        assert mesh_id.path == timeseries.full_name
    if timeseries.uuid is not None:
        assert mesh_id.id == _common._to_proto_guid(timeseries.uuid)
    if timeseries.timskey is not None:
        assert mesh_id.timeseries_key == timeseries.timskey


@pytest.mark.unittest
def test_to_proto_mesh_id_from_empty_timeseries():
    with pytest.raises(TypeError):
        _common._to_proto_mesh_id_from_timeseries(Timeseries())


@pytest.mark.unittest
@pytest.mark.parametrize(
    "resolution, expected_proto_type",
    [
        (Timeseries.Resolution.UNDEFINED, resources_pb2.Resolution.UNDEFINED),
        (Timeseries.Resolution.BREAKPOINT, resources_pb2.Resolution.BREAKPOINT),
        (Timeseries.Resolution.MIN, resources_pb2.Resolution.MIN),
        (Timeseries.Resolution.MIN5, resources_pb2.Resolution.MIN5),
        (Timeseries.Resolution.MIN10, resources_pb2.Resolution.MIN10),
        (Timeseries.Resolution.MIN15, resources_pb2.Resolution.MIN15),
        (Timeseries.Resolution.MIN30, resources_pb2.Resolution.MIN30),
        (Timeseries.Resolution.HOUR, resources_pb2.Resolution.HOUR),
        (Timeseries.Resolution.DAY, resources_pb2.Resolution.DAY),
        (Timeseries.Resolution.WEEK, resources_pb2.Resolution.WEEK),
        (Timeseries.Resolution.MONTH, resources_pb2.Resolution.MONTH),
        (Timeseries.Resolution.YEAR, resources_pb2.Resolution.YEAR),
    ],
)
def test_to_proto_resolution(resolution, expected_proto_type):
    proto_resolution = _common._to_proto_resolution(resolution)
    assert proto_resolution.type == expected_proto_type


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
