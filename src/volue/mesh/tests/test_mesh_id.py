"""
Tests for volue.mesh._mesh_id.
"""

import sys
import uuid

import pytest

from volue.mesh import Timeseries, _common, _mesh_id

from .test_utilities.utilities import (
    AttributeForTesting,
    ObjectForTesting,
    AttributeDefinitionForTesting,
)


@pytest.mark.unittest
def test_to_proto_attribute_mesh_id():
    target = uuid.uuid4()
    mesh_id = _mesh_id._to_proto_attribute_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target)

    target = "path"
    mesh_id = _mesh_id._to_proto_attribute_mesh_id(target)
    assert mesh_id.path == target

    target = AttributeForTesting()
    mesh_id = _mesh_id._to_proto_attribute_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path


@pytest.mark.unittest
@pytest.mark.parametrize(
    "target",
    [ObjectForTesting(), Timeseries(), None, 100, 100.0],
)
def test_to_proto_attribute_mesh_id_from_invalid_type(target):
    with pytest.raises(TypeError):
        _mesh_id._to_proto_attribute_mesh_id(target)


@pytest.mark.unittest
def test_to_proto_object_mesh_id():
    target = uuid.uuid4()
    mesh_id = _mesh_id._to_proto_object_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target)

    target = "path"
    mesh_id = _mesh_id._to_proto_object_mesh_id(target)
    assert mesh_id.path == target

    target = ObjectForTesting()
    mesh_id = _mesh_id._to_proto_object_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path


@pytest.mark.unittest
@pytest.mark.parametrize(
    "target",
    [AttributeForTesting(), Timeseries(), None, 100, 100.0],
)
def test_to_proto_object_mesh_id_from_invalid_type(target):
    with pytest.raises(TypeError):
        _mesh_id._to_proto_object_mesh_id(target)


@pytest.mark.unittest
def test_to_proto_read_timeseries_mesh_id():
    target = uuid.uuid4()
    mesh_id = _mesh_id._to_proto_read_timeseries_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target)

    target = "path"
    mesh_id = _mesh_id._to_proto_read_timeseries_mesh_id(target)
    assert mesh_id.path == target

    target = 100
    mesh_id = _mesh_id._to_proto_read_timeseries_mesh_id(target)
    assert mesh_id.timeseries_key == target

    target = AttributeForTesting()
    mesh_id = _mesh_id._to_proto_read_timeseries_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path


@pytest.mark.unittest
@pytest.mark.parametrize(
    "target",
    [ObjectForTesting(), Timeseries(), None, 100.0],
)
def test_to_proto_read_timeseries_mesh_id_from_invalid_type(target):
    with pytest.raises(TypeError):
        _mesh_id._to_proto_read_timeseries_mesh_id(target)


@pytest.mark.unittest
def test_to_proto_calculation_target_mesh_id():
    target = uuid.uuid4()
    mesh_id = _mesh_id._to_proto_calculation_target_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target)

    target = "path"
    mesh_id = _mesh_id._to_proto_calculation_target_mesh_id(target)
    assert mesh_id.path == target

    target = 100
    mesh_id = _mesh_id._to_proto_calculation_target_mesh_id(target)
    assert mesh_id.timeseries_key == target

    target = AttributeForTesting()
    mesh_id = _mesh_id._to_proto_calculation_target_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path

    target = ObjectForTesting()
    mesh_id = _mesh_id._to_proto_calculation_target_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path


@pytest.mark.unittest
@pytest.mark.parametrize(
    "target",
    [Timeseries(), None, 100.0],
)
def test_to_proto_calculation_target_mesh_id_from_invalid_type(target):
    with pytest.raises(TypeError):
        _mesh_id._to_proto_read_timeseries_mesh_id(target)


@pytest.mark.unittest
def test_to_proto_mesh_id():
    target = uuid.uuid4()
    mesh_id = _mesh_id._to_proto_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target)

    target = "path"
    mesh_id = _mesh_id._to_proto_mesh_id(target)
    assert mesh_id.path == target

    target = 100
    mesh_id = _mesh_id._to_proto_mesh_id(target)
    assert mesh_id.timeseries_key == target

    target = AttributeForTesting()
    mesh_id = _mesh_id._to_proto_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path

    target = ObjectForTesting()
    mesh_id = _mesh_id._to_proto_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path

    target = AttributeDefinitionForTesting()
    mesh_id = _mesh_id._to_proto_mesh_id(target)
    assert mesh_id.id == _common._to_proto_guid(target.id)
    assert mesh_id.path == target.path


@pytest.mark.unittest
@pytest.mark.parametrize(
    "target",
    [Timeseries(), None, 100.0],
)
def test_to_proto_mesh_id_from_invalid_type(target):
    with pytest.raises(TypeError, match="invalid target type"):
        _mesh_id._to_proto_mesh_id(target)


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
