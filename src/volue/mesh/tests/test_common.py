"""
Tests for volue.mesh._common.
"""

import sys
import uuid

import pytest

from volue.mesh import Timeseries, _common

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

if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
