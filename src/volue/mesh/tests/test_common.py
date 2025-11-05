"""
Tests for volue.mesh._common.
"""

import sys
import uuid

import pytest

from volue.mesh import Timeseries, _common
from volue.mesh._version_compatibility import to_parsed_version


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

def test_to_parsed_version():
    parsed = to_parsed_version("99.0.0+0")
    assert parsed is not None
    assert parsed.major == 99 and parsed.minor == 0 and parsed.patch == 0

    parsed = to_parsed_version("2.20.0")
    assert parsed is not None
    assert parsed.major == 2 and parsed.minor == 20 and parsed.patch == 0

    parsed = to_parsed_version("01.01.01")
    assert parsed is not None
    assert parsed.major == 1 and parsed.minor == 1 and parsed.patch == 1

    parsed = to_parsed_version("2.20")
    assert parsed is None

    parsed = to_parsed_version("-1.0.0")
    assert parsed is None

    parsed = to_parsed_version("a.0.0")
    assert parsed is None

    parsed = to_parsed_version("0,0.0")
    assert parsed is None

    parsed = to_parsed_version("")
    assert parsed is None


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
