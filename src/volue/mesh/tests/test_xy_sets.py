import datetime
import operator

import dateutil
import sys
import uuid

import grpc
import pytest

from volue import mesh
import volue.mesh.aio



OBJECT_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
UNVERSIONED_PATH = OBJECT_PATH + ".XYSetAtt"
VERSIONED_PATH = OBJECT_PATH + ".XYZSeriesAtt"


def generate_xy_set(seed, valid_from_time=None):
    curves = [mesh.XyCurve(z, [(v, -v) for v in range(seed)])
              for z in range(seed)]
    return mesh.XySet(valid_from_time, curves)


@pytest.mark.database
def test_get_empty_xy_set_unversioned(session):
    xy_sets = session.get_xy_sets(target=UNVERSIONED_PATH)

    # Unversioned XY set attributes always have one XY set
    assert len(xy_sets) == 1

    # Unversioned XY set attributes never have validity
    assert xy_sets[0].valid_from_time is None

    # An empty attribute never has curves
    assert len(xy_sets[0].xy_curves) == 0


@pytest.mark.database
def test_update_xy_sets_unversioned(session):
    # An empty update will reset the value of an unversioned XY set attribute.
    # This will not remove the value, but make it empty.
    #
    # In this case this is a no-op.
    session.update_xy_sets(target=UNVERSIONED_PATH, new_xy_sets=[])

    xy_sets = session.get_xy_sets(target=UNVERSIONED_PATH)
    assert len(xy_sets) == 1
    assert len(xy_sets[0].xy_curves) == 0

    # An update with one XY set will set the value of the attribute to that
    # XY set.
    value = generate_xy_set(3)
    session.update_xy_sets(target=UNVERSIONED_PATH, new_xy_sets=[value])

    xy_sets = session.get_xy_sets(target=UNVERSIONED_PATH)
    assert len(xy_sets) == 1
    assert xy_sets[0] == value

    # Clear the attribute again.
    session.update_xy_sets(target=UNVERSIONED_PATH, new_xy_sets=[])
    xy_sets = session.get_xy_sets(target=UNVERSIONED_PATH)
    assert len(xy_sets) == 1
    assert len(xy_sets[0].xy_curves) == 0


@pytest.mark.database
def test_update_xy_sets_unsorted_z(session):
    curves = [mesh.XyCurve(14.3, []),
              mesh.XyCurve(3.8, []),
              mesh.XyCurve(900.4, []),
              mesh.XyCurve(-100.0, [])]

    session.update_xy_sets(target=UNVERSIONED_PATH, new_xy_sets=[mesh.XySet(None, curves)])
    xy_sets = session.get_xy_sets(target=UNVERSIONED_PATH)
    assert len(xy_sets) == 1
    # The server always returns sorted z-values.
    assert xy_sets[0].xy_curves == sorted(curves, key=operator.attrgetter("z"))


@pytest.mark.database
def test_update_xy_sets_versioned(session):
    start_time = datetime.datetime.fromisoformat("1965-10-10").replace(tzinfo=dateutil.tz.UTC)
    end_time = datetime.datetime.fromisoformat("1975-10-10").replace(tzinfo=dateutil.tz.UTC)

    kwargs = {"target": VERSIONED_PATH, "start_time": start_time, "end_time": end_time}

    # No-op update
    session.update_xy_sets(**kwargs)

    # Add an XY set at start
    value = generate_xy_set(3, start_time)
    session.update_xy_sets(new_xy_sets=[value], **kwargs)
    xy_sets = session.get_xy_sets(**kwargs)
    assert len(xy_sets) == 1
    assert xy_sets[0] == value

    # Remove that XY set
    session.update_xy_sets(**kwargs)
    xy_sets = session.get_xy_sets(**kwargs)
    assert len(xy_sets) == 0

    values = []
    valid_from_time = start_time
    for i in range(10):
        values.append(generate_xy_set(i, valid_from_time))
        valid_from_time = valid_from_time.replace(year=valid_from_time.year + 1)

    # Add multiple XY sets, one operation
    session.update_xy_sets(new_xy_sets=values, **kwargs)
    xy_sets = session.get_xy_sets(**kwargs)
    assert xy_sets == values

    # Remove that XY set
    session.update_xy_sets(**kwargs)
    xy_sets = session.get_xy_sets(**kwargs)
    assert len(xy_sets) == 0

    # Add multiple XY sets, multiple operations
    for xy_set in values:
        session.update_xy_sets(VERSIONED_PATH, xy_set.valid_from_time, end_time,
                                    new_xy_sets=[xy_set])

    xy_sets = session.get_xy_sets(**kwargs)
    assert xy_sets == values


@pytest.mark.database
def test_update_xy_set_invalid_input_unversioned(session):
    # Target is required, and checked client-side.
    with pytest.raises(TypeError):
        session.update_xy_sets()

    now = datetime.datetime.now()

    # start_time and end_time must both be valid or both None

    with pytest.raises(TypeError):
        session.update_xy_sets(target=UNVERSIONED_PATH, start_time=now)

    with pytest.raises(TypeError):
        session.update_xy_sets(target=UNVERSIONED_PATH, end_time=now)

    # target must exist

    with pytest.raises(grpc.RpcError, match="attribute not found"):
        session.update_xy_sets(target="")

    with pytest.raises(grpc.RpcError, match="attribute not found"):
        session.update_xy_sets(target=uuid.uuid4())

    # target must be an XY set attribute
    with pytest.raises(grpc.RpcError, match="unexpected kind"):
        session.update_xy_sets(target=OBJECT_PATH)

    # start_time, end_time cannot be used with unversioned attributes
    with pytest.raises(grpc.RpcError, match="interval must be empty when updating XYSetAttribute"):
        session.update_xy_sets(target=UNVERSIONED_PATH,
                                    start_time=now, end_time=now)

    # Multiple XY sets cannot be set on unversioned attributes
    with pytest.raises(grpc.RpcError, match="xy_sets must have zero or one element"):
        session.update_xy_sets(target=UNVERSIONED_PATH,
                                    new_xy_sets=[mesh.XySet(None, []), mesh.XySet(None, [])])

    # BUG: Mesh 2.5.2 silently ignores valid_from_time, in the future this
    # will cause an error.
    session.update_xy_sets(target=UNVERSIONED_PATH,
                                new_xy_sets=[mesh.XySet(now, [])])


@pytest.mark.database
def test_update_xy_set_invalid_input_versioned(session):
    # start_time, end_time must be used with versioned attributes
    with pytest.raises(grpc.RpcError, match="interval must have a value when updating XYZSeriesAttribute"):
        session.update_xy_sets(target=VERSIONED_PATH)

    now = datetime.datetime.now(dateutil.tz.UTC)
    later = now + datetime.timedelta(days=365)

    # [start_time, end_time) must be a valid interval
    with pytest.raises(grpc.RpcError, match="UtcInterval .* is invalid, start_time > end_time"):
        session.update_xy_sets(target=VERSIONED_PATH, start_time=later, end_time=now)

    kwargs = {"target": VERSIONED_PATH, "start_time": now, "end_time": later}

    # valid_from_time must be set on new XY sets
    with pytest.raises(grpc.RpcError, match="must have a valid_from_time"):
        session.update_xy_sets(new_xy_sets=[mesh.XySet(None, [])], **kwargs)

    # One XySet cannot have curves with duplicate reference values

    with pytest.raises(grpc.RpcError, match="duplicate reference value"):
        value = mesh.XySet(now, [mesh.XyCurve(0, []), mesh.XyCurve(0, [])])
        session.update_xy_sets(new_xy_sets=[value], **kwargs)

    with pytest.raises(grpc.RpcError, match="duplicate reference value"):
        value = mesh.XySet(now, [mesh.XyCurve(0, []), mesh.XyCurve(1, []), mesh.XyCurve(0, [])])
        session.update_xy_sets(new_xy_sets=[value], **kwargs)

    # New XySets must be within interval
    even_later = later + datetime.timedelta(days=365)
    with pytest.raises(grpc.RpcError, match="within .* interval"):
        session.update_xy_sets(new_xy_sets=[mesh.XySet(even_later, [])], **kwargs)

    # Multiple XySets cannot have the same valid_from_times
    value = mesh.XySet(now, [])
    with pytest.raises(grpc.RpcError, match="duplicate timestamps"):
        session.update_xy_sets(new_xy_sets=[value, value], **kwargs)


@pytest.mark.asyncio
@pytest.mark.database
async def test_xy_async(async_session):
    xy_sets = await async_session.get_xy_sets(UNVERSIONED_PATH)
    assert xy_sets == [mesh.XySet(None, [])]

    # Create an update task, but don't run it.
    new_xy_sets = [generate_xy_set(3)]
    future_update = async_session.update_xy_sets(UNVERSIONED_PATH, new_xy_sets=new_xy_sets)

    # Still empty.
    xy_sets = await async_session.get_xy_sets(UNVERSIONED_PATH)
    assert xy_sets == [mesh.XySet(None, [])]

    # Run the update.
    await future_update

    # And now we should have data.
    xy_sets = await async_session.get_xy_sets(UNVERSIONED_PATH)
    assert xy_sets == new_xy_sets


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
