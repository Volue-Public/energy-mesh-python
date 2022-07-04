import datetime
import dateutil
import sys
import uuid

import grpc
import pytest

from volue import mesh

OBJECT_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
UNVERSIONED_PATH = OBJECT_PATH + ".XYSetAtt"
VERSIONED_PATH = OBJECT_PATH + ".XYZSeriesAtt"


@pytest.fixture(scope="module")
def mesh_connection():
    return mesh.Connection.insecure("127.0.0.1:50051")


@pytest.fixture
def mesh_session(mesh_connection):
    with mesh_connection.create_session() as session:
        yield session


def generate_xy_set(seed, valid_from_time=None):
    curves = [mesh.XyCurve(z, [(v, -v) for v in range(seed)])
              for z in range(seed)]
    return mesh.XySet(valid_from_time, curves)


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
def test_update_xy_sets_versioned(mesh_session):
    start_time = datetime.datetime.fromisoformat("1965-10-10").replace(tzinfo=dateutil.tz.UTC)
    end_time = datetime.datetime.fromisoformat("1975-10-10").replace(tzinfo=dateutil.tz.UTC)

    kwargs = {"target": VERSIONED_PATH, "start_time": start_time, "end_time": end_time}

    # No-op update
    mesh_session.update_xy_sets(**kwargs)

    # Add an XY set at start
    value = generate_xy_set(3, start_time)
    mesh_session.update_xy_sets(new_xy_sets=[value], **kwargs)
    xy_sets = mesh_session.get_xy_sets(**kwargs)
    assert len(xy_sets) == 1
    assert xy_sets[0] == value

    # Remove that XY set
    mesh_session.update_xy_sets(**kwargs)
    xy_sets = mesh_session.get_xy_sets(**kwargs)
    assert len(xy_sets) == 0

    values = []
    valid_from_time = start_time
    for i in range(10):
        values.append(generate_xy_set(i, valid_from_time))
        valid_from_time = valid_from_time.replace(year=valid_from_time.year + 1)

    # Add multiple XY sets, one operation
    mesh_session.update_xy_sets(new_xy_sets=values, **kwargs)
    xy_sets = mesh_session.get_xy_sets(**kwargs)
    assert xy_sets == values

    # Remove that XY set
    mesh_session.update_xy_sets(**kwargs)
    xy_sets = mesh_session.get_xy_sets(**kwargs)
    assert len(xy_sets) == 0

    # Add multiple XY sets, multiple operations
    for xy_set in values:
        mesh_session.update_xy_sets(VERSIONED_PATH, xy_set.valid_from_time, end_time,
                                    new_xy_sets=[xy_set])

    xy_sets = mesh_session.get_xy_sets(**kwargs)
    assert xy_sets == values


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


@pytest.mark.server
def test_update_xy_set_invalid_input_versioned(mesh_session):
    # start_time, end_time must be used with versioned attributes
    with pytest.raises(grpc.RpcError, match="interval must have a value when updating XYZSeriesAttribute"):
        mesh_session.update_xy_sets(target=VERSIONED_PATH)

    now = datetime.datetime.now(dateutil.tz.UTC)
    later = now + datetime.timedelta(days=365)

    # [start_time, end_time) must be a valid interval
    with pytest.raises(grpc.RpcError, match="UtcInterval .* is invalid, start_time > end_time"):
        mesh_session.update_xy_sets(target=VERSIONED_PATH, start_time=later, end_time=now)

    kwargs = {"target": VERSIONED_PATH, "start_time": now, "end_time": later}

    # valid_from_time must be set on new XY sets
    with pytest.raises(grpc.RpcError, match="must have a valid_from_time"):
        mesh_session.update_xy_sets(new_xy_sets=[mesh.XySet(None, [])], **kwargs)

    # One XySet cannot have curves with duplicate reference values

    with pytest.raises(grpc.RpcError, match="duplicate reference value"):
        value = mesh.XySet(now, [mesh.XyCurve(0, []), mesh.XyCurve(0, [])])
        mesh_session.update_xy_sets(new_xy_sets=[value], **kwargs)

    with pytest.raises(grpc.RpcError, match="duplicate reference value"):
        value = mesh.XySet(now, [mesh.XyCurve(0, []), mesh.XyCurve(1, []), mesh.XyCurve(0, [])])
        mesh_session.update_xy_sets(new_xy_sets=[value], **kwargs)

    # New XySets must be within interval
    even_later = later + datetime.timedelta(days=365)
    with pytest.raises(grpc.RpcError, match="within .* interval"):
        mesh_session.update_xy_sets(new_xy_sets=[mesh.XySet(even_later, [])], **kwargs)

    # Multiple XySets cannot have the same valid_from_times
    value = mesh.XySet(now, [])
    with pytest.raises(grpc.RpcError, match="duplicate timestamps"):
        mesh_session.update_xy_sets(new_xy_sets=[value, value], **kwargs)


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
