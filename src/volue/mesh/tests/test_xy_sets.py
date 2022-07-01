import datetime
import sys
import uuid

import grpc
import pytest

from volue import mesh

OBJECT_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
UNVERSIONED_PATH = OBJECT_PATH + ".XYSetAtt"


@pytest.fixture(scope="module")
def mesh_connection():
    return mesh.Connection.insecure("127.0.0.1:50051")


@pytest.fixture
def mesh_session(mesh_connection):
    with mesh_connection.create_session() as session:
        yield session


def generate_xy_set(seed):
    curves = [mesh.XyCurve(z, [(v, -v) for v in range(seed)])
              for z in range(seed)]
    return mesh.XySet(None, curves)


@pytest.mark.server
def test_get_empty_xy_set_unversioned(mesh_session):
    xy_sets = mesh_session.get_xy_sets(target=UNVERSIONED_PATH)

    # Unversioned XY set attributes always have one XY set
    assert len(xy_sets) == 1

    # Unversioned XY set attributes never have validity
    assert xy_sets[0].valid_from_time is None

    # An empty attribute never has curves
    assert len(xy_sets[0].xy_curves) == 0


@pytest.mark.server
def test_update_xy_sets_unversioned(mesh_session):
    # An empty update will reset the value of an unversioned XY set attribute.
    # This will not remove the value, but make it empty.
    #
    # In this case this is a no-op.
    mesh_session.update_xy_sets(target=UNVERSIONED_PATH, new_xy_sets=[])

    xy_sets = mesh_session.get_xy_sets(target=UNVERSIONED_PATH)
    assert len(xy_sets) == 1
    assert len(xy_sets[0].xy_curves) == 0

    # An update with one XY set will set the value of the attribute to that
    # XY set.
    value = generate_xy_set(3)
    mesh_session.update_xy_sets(target=UNVERSIONED_PATH, new_xy_sets=[value])

    xy_sets = mesh_session.get_xy_sets(target=UNVERSIONED_PATH)
    assert len(xy_sets) == 1
    assert xy_sets[0] == value

    # Clear the attribute again.
    mesh_session.update_xy_sets(target=UNVERSIONED_PATH, new_xy_sets=[])
    xy_sets = mesh_session.get_xy_sets(target=UNVERSIONED_PATH)
    assert len(xy_sets) == 1
    assert len(xy_sets[0].xy_curves) == 0


@pytest.mark.server
def test_update_xy_set_invalid_input_unversioned(mesh_session):
    # Target is required, and checked client-side.
    with pytest.raises(TypeError):
        mesh_session.update_xy_sets()

    now = datetime.datetime.now()

    # start_time and end_time must both be valid or both None

    with pytest.raises(TypeError):
        mesh_session.update_xy_sets(target=UNVERSIONED_PATH, start_time=now)

    with pytest.raises(TypeError):
        mesh_session.update_xy_sets(target=UNVERSIONED_PATH, end_time=now)

    # target must exist

    with pytest.raises(grpc.RpcError, match="attribute not found"):
        mesh_session.update_xy_sets(target="")

    with pytest.raises(grpc.RpcError, match="attribute not found"):
        mesh_session.update_xy_sets(target=uuid.uuid4())

    # target must be an XY set attribute
    with pytest.raises(grpc.RpcError, match="unexpected kind"):
        mesh_session.update_xy_sets(target=OBJECT_PATH)

    # start_time, end_time cannot be used with unversioned attributes
    with pytest.raises(grpc.RpcError, match="interval must be empty when updating XYSetAttribute"):
        mesh_session.update_xy_sets(target=UNVERSIONED_PATH,
                                    start_time=now, end_time=now)

    # Multiple XY sets cannot be set on unversioned attributes
    with pytest.raises(grpc.RpcError, match="xy_sets must have zero or one element"):
        mesh_session.update_xy_sets(target=UNVERSIONED_PATH,
                                    new_xy_sets=[mesh.XySet(None, []), mesh.XySet(None, [])])

    # BUG: Mesh 2.5.2 silently ignores valid_from_time, in the future this
    # will cause an error.
    mesh_session.update_xy_sets(target=UNVERSIONED_PATH,
                                new_xy_sets=[mesh.XySet(now, [])])


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
