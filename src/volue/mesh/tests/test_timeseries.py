"""
Tests for volue.mesh.Timeseries
"""

import math
import sys
import uuid
from datetime import datetime, timedelta

import grpc
import pandas as pd
import pyarrow as pa
import pytest
from dateutil import tz

from volue.mesh import Timeseries
from volue.mesh._common import _to_proto_guid, _to_proto_timeseries
from volue.mesh.proto.time_series.v1alpha import time_series_pb2
from volue.mesh.proto.type import resources_pb2

TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.TsRawAtt"
TIME_SERIES_ATTRIBUTE_WITH_CALCULATION_PATH = (
    "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1.TsCalcAtt"
)
TIME_SERIES_START_TIME = datetime(2016, 1, 1, 1)
TIME_SERIES_END_TIME = datetime(2016, 1, 1, 9)


def get_test_time_series_pyarrow_table(
    first_point_timestamp: datetime = TIME_SERIES_START_TIME,
    last_point_timestamp: datetime = TIME_SERIES_END_TIME,
):
    """Returns an Arrow table to be used for writing time series."""
    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]
    utc_times = pd.date_range(
        first_point_timestamp, last_point_timestamp, freq="1h"
    ).tolist()
    flags = [Timeseries.PointFlags.OK.value] * len(utc_times)
    points = list(range(10, 10 + 2 * len(utc_times), 2))

    arrays = [pa.array(utc_times), pa.array(flags), pa.array(points)]
    return pa.Table.from_arrays(arrays, schema=Timeseries.schema)


def verify_physical_timeseries(reply_timeseries: Timeseries):
    """
    Verify if all time series properties and data have expected values.
    "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.TsRawAtt"
    """
    assert reply_timeseries.resolution == Timeseries.Resolution.HOUR

    assert type(reply_timeseries) is Timeseries
    assert reply_timeseries.number_of_points == 9

    # check timestamps
    utc_date = reply_timeseries.arrow_table[0]
    for count, item in enumerate(utc_date):
        assert item.as_py() == datetime(2016, 1, 1, count + 1, 0)

    # check flags and values
    flags = reply_timeseries.arrow_table[1]
    values = reply_timeseries.arrow_table[2]

    for number in range(9):
        if number == 3:
            assert math.isnan(values[3].as_py())
            assert (
                flags[3].as_py()
                == Timeseries.PointFlags.NOT_OK.value
                | Timeseries.PointFlags.MISSING.value
            )
        else:
            assert values[number].as_py() == (number + 1) * 100
            assert flags[number].as_py() == Timeseries.PointFlags.OK.value


def verify_calculation_timeseries(reply_timeseries: Timeseries):
    """
    Verify if all time series properties and data have expected values.
    "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1.TsCalcAtt"
    """
    assert type(reply_timeseries) is Timeseries
    assert reply_timeseries.number_of_points == 9

    # check timestamps
    utc_date = reply_timeseries.arrow_table[0]
    for count, item in enumerate(utc_date):
        assert item.as_py() == datetime(2016, 1, 1, count + 1, 0)

    # check flags and values
    flags = reply_timeseries.arrow_table[1]
    values = reply_timeseries.arrow_table[2]

    for number in range(9):
        if number == 3:
            assert values[number].as_py() == 1000
        else:
            assert values[number].as_py() == (number + 1) + 1000
        assert flags[number].as_py() == Timeseries.PointFlags.SUSPECT.value


def get_targets(session, attribute_path):
    """
    Return all possible targets for reading time series, like: ID, path or time
    series key.
    """
    # ID is auto-generated when creating an attribute, so
    # first we need to read it.
    attribute = session.get_timeseries_attribute(attribute_path)
    targets = [attribute.id, attribute_path, attribute]

    if attribute.time_series_resource is not None:
        targets.append(attribute.time_series_resource.timeseries_key)

    return targets


@pytest.mark.unittest
def test_can_create_empty_timeserie():
    """Check that an empty time series can be created."""
    ts = Timeseries()
    assert ts is not None


@pytest.mark.unittest
def test_can_create_timeserie_from_existing_data():
    """Check that a time series can be created from existing data."""

    arrays = [
        pa.array(
            [datetime(2016, 5, 1), datetime(2016, 5, 1, 1), datetime(2016, 5, 1, 2)],
            type=pa.timestamp("ms"),
        ),
        pa.array([0, 0, 0], type=pa.uint32()),
        pa.array([0.0, 0.0, 0.0]),
    ]
    table = pa.Table.from_arrays(arrays=arrays, names=["utc_time", "flags", "value"])
    time_series = Timeseries(table)
    assert time_series.number_of_points == 3


@pytest.mark.unittest
def test_init_timeseries_with_wrong_pyarrow_table_schema_should_throw():
    """Check that a time series can't be created with invalid PyArrow table schema."""

    arrays = [
        pa.array(["one", "two", "three", "four", "five"]),
        pa.array([1, 2, 3, 4, 5]),
        pa.array([6, 7, 8, 9, 10]),
    ]

    table = pa.Table.from_arrays(
        arrays=arrays, names=["name", "first_list", "second_list"]
    )
    with pytest.raises(TypeError, match="invalid PyArrow table schema"):
        Timeseries(table)

    # schema names are correct, but types not - still should be an error
    table = pa.Table.from_arrays(arrays=arrays, names=["utc_time", "flags", "value"])
    with pytest.raises(TypeError, match="invalid PyArrow table schema"):
        Timeseries(table)


@pytest.mark.unittest
def test_can_serialize_and_deserialize_write_timeserie_request():
    """Check that timeseries can be de-/serialized."""

    start = datetime(
        year=2013, month=7, day=25, hour=0, minute=0, second=0
    )  # 25/07/2013 00:00:00
    end = datetime(
        year=2016, month=12, day=25, hour=0, minute=0, second=0
    )  # 25/12/2016 00:00:00

    arrays = [
        pa.array(
            [datetime(2016, 5, 1), datetime(2016, 5, 1, 1), datetime(2016, 5, 1, 2)]
        ),
        pa.array([0, 0, 0]),
        pa.array([0.0, 0.0, 0.0]),
    ]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    original_timeseries = Timeseries(
        table=table,
        resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
        start_time=start,
        end_time=end,
        timskey=1,
        uuid_id=uuid.uuid4(),
        full_name="some_name",
    )

    assert original_timeseries.start_time == start
    assert original_timeseries.end_time == end

    original_proto_timeseries = _to_proto_timeseries(original_timeseries)
    session_id_original = _to_proto_guid(uuid.uuid4())

    original_reply = time_series_pb2.WriteTimeseriesRequest(
        session_id=session_id_original, timeseries=original_proto_timeseries
    )

    binary_data = original_reply.SerializeToString()
    assert binary_data is not None

    reply = time_series_pb2.WriteTimeseriesRequest()
    reply.ParseFromString(binary_data)
    assert original_reply == reply
    assert session_id_original == reply.session_id
    assert original_proto_timeseries == reply.timeseries

    reader = pa.ipc.open_stream(reply.timeseries.data)
    table = reader.read_all()
    assert original_timeseries.arrow_table == table
    assert original_timeseries.arrow_table[0] == table[0]
    assert original_timeseries.arrow_table[1] == table[1]
    assert original_timeseries.arrow_table[2] == table[2]


@pytest.mark.unittest
def test_timeseries_without_explicit_start_end_datetime_will_deduct_it_from_pyarrow_table():
    """
    Check that a time series can be created without providing
    explicitly `start_time` and `end_time` arguments. In such
    case it should set them based on PyArrow table data.
    `start_time` equals first PyArrow table timestamp
    `end_time` equals last PyArrow table timestamp + 1 second as it
    must be greater than last time point to be written.
    """

    arrays = [
        pa.array(
            [datetime(2016, 5, 1), datetime(2016, 5, 1, 1), datetime(2016, 5, 1, 2)]
        ),
        pa.array([0, 0, 0]),
        pa.array([0.0, 0.0, 0.0]),
    ]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    time_series = Timeseries(
        table=table,
        resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
        timskey=1,
        uuid_id=uuid.uuid4(),
        full_name="some_name",
    )
    assert time_series.start_time == datetime(2016, 5, 1)
    assert time_series.end_time == datetime(2016, 5, 1, 2) + timedelta(seconds=1)


@pytest.mark.unittest
def test_timeseries_without_explicit_start_end_datetime_and_pyarrow_table():
    """
    Check that a time series can be created without providing
    explicitly `start_time`, `end_time` and PyArrow `table` arguments.
    """

    time_series = Timeseries(
        resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
        timskey=1,
        uuid_id=uuid.uuid4(),
        full_name="some_name",
    )
    assert time_series.number_of_points == 0


@pytest.mark.unittest
def test_timeseries_without_explicit_start_end_datetime_and_empty_pyarrow_table():
    """
    Check that a time series can be created without providing
    explicitly `start_time`, `end_time` and PyArrow `table` arguments.
    """

    arrays = [pa.array([]), pa.array([]), pa.array([])]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    time_series = Timeseries(
        table=table,
        resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
        timskey=1,
        uuid_id=uuid.uuid4(),
        full_name="some_name",
    )
    assert time_series.number_of_points == 0


@pytest.mark.database
def test_read_physical_timeseries_points(session):
    """
    Check that timeseries points can be read from physical time series using
    time series key, time series attribute ID, time series attribute path and
    time series attribute instance.

    Note: The time series attribute needs to be connected to the given physical
          time series.
    """

    targets = get_targets(session, TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH)

    for target in targets:
        reply_timeseries = session.read_timeseries_points(
            target, TIME_SERIES_START_TIME, TIME_SERIES_END_TIME
        )
        verify_physical_timeseries(reply_timeseries)

        # If we are reading physical time series by time series attribute
        # (path, ID or object) then no time series key is returned (meaning 0).
        # If we are reading physical time series directly via time series key,
        # then the key should be returned.
        expected_timeseries_key = target if isinstance(target, int) else 0
        assert reply_timeseries.timskey == expected_timeseries_key


@pytest.mark.database
def test_read_calculation_timeseries_points(session):
    """
    Check that timeseries points can be read from time series attribute with
    calculation expression using time series attribute ID, time series
    attribute path and time series attribute instance.
    """

    targets = get_targets(session, TIME_SERIES_ATTRIBUTE_WITH_CALCULATION_PATH)

    for target in targets:
        reply_timeseries = session.read_timeseries_points(
            target, TIME_SERIES_START_TIME, TIME_SERIES_END_TIME
        )
        verify_calculation_timeseries(reply_timeseries)


def get_different_time_zone_datetimes(datetime):
    """
    Returns list containing datetimes:
    * time zone naive
    * time zone aware (UTC)
    * converted to local time zone
    """

    # confirm input datetime is time zone naive
    assert datetime.tzinfo is None
    # replace to UTC, because we treat time zone naive datetime as UTC
    datetime_utc = datetime.replace(tzinfo=tz.UTC)
    # now we can convert to different time zones (from time zone aware UTC datetime)
    datetime_local = datetime_utc.astimezone(tz.gettz("Europe/Warsaw"))

    return [
        datetime,  # time zone naive
        datetime_utc,  # UTC
        datetime_local,  # local time zone
    ]


@pytest.mark.database
@pytest.mark.parametrize(
    "start_time", get_different_time_zone_datetimes(TIME_SERIES_START_TIME)
)
@pytest.mark.parametrize(
    "end_time", get_different_time_zone_datetimes(TIME_SERIES_END_TIME)
)
def test_read_timeseries_points_with_different_datetime_timezones(
    session, start_time, end_time
):
    """
    Check that timeseries points read accepts time zone aware and
    naive (treated as UTC) datetimes as input arguments.
    """
    reply_timeseries = session.read_timeseries_points(
        TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH, start_time, end_time
    )
    verify_physical_timeseries(reply_timeseries)
    assert reply_timeseries.timskey == 0


@pytest.mark.database
def test_write_timeseries_points(session):
    """
    Check that time series can be written to the server using time series key,
    time series attribute ID and time series attribute path.
    """

    new_table = get_test_time_series_pyarrow_table()

    attribute_path = TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH
    attribute = session.get_timeseries_attribute(attribute_path)

    test_cases = [
        Timeseries(table=new_table, full_name=attribute_path),
        Timeseries(table=new_table, uuid_id=attribute.id),
        Timeseries(
            table=new_table, timskey=attribute.time_series_resource.timeseries_key
        ),
    ]

    for test_case in test_cases:
        session.write_timeseries_points(test_case)

        reply_timeseries = session.read_timeseries_points(
            target=attribute_path,
            start_time=TIME_SERIES_START_TIME,
            end_time=TIME_SERIES_END_TIME,
        )

        assert new_table == reply_timeseries.arrow_table

        session.rollback()


@pytest.mark.database
def test_write_one_timeseries_point(session):
    """
    Check that writing one time series point succeeds and does not affect
    already existing adjacent points.
    """

    utc_times = [datetime(2016, 1, 1, 4)]
    flags = [Timeseries.PointFlags.OK.value]
    points = [400]

    arrays = [pa.array(utc_times), pa.array(flags), pa.array(points)]
    new_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    attribute_path = TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH
    session.write_timeseries_points(
        Timeseries(table=new_table, full_name=attribute_path)
    )

    reply_timeseries = session.read_timeseries_points(
        target=attribute_path,
        start_time=TIME_SERIES_START_TIME,
        end_time=TIME_SERIES_END_TIME,
    )

    # check timestamps
    utc_date = reply_timeseries.arrow_table[0]
    for count, item in enumerate(utc_date):
        assert item.as_py() == datetime(2016, 1, 1, count + 1, 0)

    # check flags and values
    flags = reply_timeseries.arrow_table[1]
    values = reply_timeseries.arrow_table[2]

    for number in range(9):
        assert values[number].as_py() == (number + 1) * 100
        assert flags[number].as_py() == Timeseries.PointFlags.OK.value


@pytest.mark.database
def test_remove_timeseries_points(session):
    empty_table = Timeseries.schema.empty_table()

    attribute_path = TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH
    session.write_timeseries_points(
        Timeseries(
            table=empty_table,
            start_time=TIME_SERIES_START_TIME,
            end_time=TIME_SERIES_END_TIME + timedelta(hours=1),
            full_name=attribute_path,
        )
    )

    reply_timeseries = session.read_timeseries_points(
        target=attribute_path,
        start_time=TIME_SERIES_START_TIME,
        end_time=TIME_SERIES_END_TIME,
    )

    # check timestamps
    utc_date = reply_timeseries.arrow_table[0]
    for count, item in enumerate(utc_date):
        assert item.as_py() == datetime(2016, 1, 1, count + 1, 0)

    # check flags and values
    flags = reply_timeseries.arrow_table[1]
    values = reply_timeseries.arrow_table[2]

    for i in range(9):
        assert math.isnan(values[i].as_py())
        assert flags[i].as_py() == Timeseries.PointFlags.MISSING.value


@pytest.mark.database
def test_remove_timeseries_points_without_providing_write_interval(session):
    empty_table = Timeseries.schema.empty_table()

    attribute_path = TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH

    with pytest.raises(
        AttributeError,
        match="'Timeseries' object has no attribute 'start_time'",
    ):
        session.write_timeseries_points(
            Timeseries(
                table=empty_table,
                end_time=TIME_SERIES_END_TIME + timedelta(hours=1),
                full_name=attribute_path,
            )
        )

    with pytest.raises(
        AttributeError,
        match="'Timeseries' object has no attribute 'start_time'",
    ):
        session.write_timeseries_points(
            Timeseries(
                table=empty_table,
                full_name=attribute_path,
            )
        )

    with pytest.raises(
        AttributeError,
        match="'Timeseries' object has no attribute 'end_time'",
    ):
        session.write_timeseries_points(
            Timeseries(
                table=empty_table,
                start_time=TIME_SERIES_START_TIME,
                full_name=attribute_path,
            )
        )


@pytest.mark.database
def test_write_timeseries_point_from_other_session(connection):
    """
    Check that writing one time series point succeeds and that a dependent
    calculation time series is correctly updated in different session.
    """

    # create two separate sessions
    writer_session = connection.create_session()
    reader_session = connection.create_session()
    writer_session.open()
    reader_session.open()

    # first read in one session a calculation time series
    reply_timeseries = reader_session.read_timeseries_points(
        target=TIME_SERIES_ATTRIBUTE_WITH_CALCULATION_PATH,
        start_time=datetime(2016, 1, 1, 1),
        end_time=datetime(2016, 1, 1, 4),
    )
    # it is a piecewise linear time series, so for approximation purposes Mesh
    # returns also one point after the requested interval
    assert reply_timeseries.number_of_points == 4

    point_new_value = 50

    # in one session we will update a physical time series
    new_point_timestamp = datetime(2016, 1, 1, 3)
    utc_times = [new_point_timestamp]
    flags = [Timeseries.PointFlags.OK.value]
    points = [point_new_value]
    arrays = [pa.array(utc_times), pa.array(flags), pa.array(points)]
    new_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    attribute_path_for_writing = (
        "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1.TsRawAtt"
    )
    writer_session.write_timeseries_points(
        Timeseries(table=new_table, full_name=attribute_path_for_writing)
    )
    # commit the changes so that other session will have access to changed data
    writer_session.commit()

    # now read a calculation time series again
    reply_timeseries = reader_session.read_timeseries_points(
        target=TIME_SERIES_ATTRIBUTE_WITH_CALCULATION_PATH,
        start_time=new_point_timestamp,
        end_time=datetime(2016, 1, 1, 4),
    )

    # check if point written in the other session is visible in the calculation
    values = reply_timeseries.arrow_table[2]
    assert values[0].as_py() == point_new_value + 1000

    # write original value back
    points = [3]
    arrays = [pa.array(utc_times), pa.array(flags), pa.array(points)]
    new_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    writer_session.write_timeseries_points(
        Timeseries(table=new_table, full_name=attribute_path_for_writing)
    )
    writer_session.commit()

    # check if we correctly wrote the original values back
    # by verifying calculation time series that depend on them
    reply_timeseries = reader_session.read_timeseries_points(
        target=TIME_SERIES_ATTRIBUTE_WITH_CALCULATION_PATH,
        start_time=TIME_SERIES_START_TIME,
        end_time=TIME_SERIES_END_TIME,
    )
    verify_calculation_timeseries(reply_timeseries)


@pytest.mark.database
def test_write_timeseries_points_to_calculation_timeseries(session):
    """
    Check that writing time series points to a time series attribute without
    a connected physical time series will throw.
    """

    new_table = get_test_time_series_pyarrow_table()
    timeseries = Timeseries(
        table=new_table, full_name=TIME_SERIES_ATTRIBUTE_WITH_CALCULATION_PATH
    )

    with pytest.raises(grpc.RpcError, match="not found"):
        session.write_timeseries_points(timeseries)


@pytest.mark.database
def test_write_unsorted_timeseries_points(session):
    """
    Check that writing unsorted (by timestamp) time series points to a time
    series attribute will throw.
    """

    utc_times = [
        datetime(2020, 1, 1),
        datetime(2020, 1, 3),
        datetime(2020, 1, 2),
        datetime(2020, 1, 4),
    ]
    flags = [Timeseries.PointFlags.OK.value] * len(utc_times)
    points = list(range(len(utc_times)))

    arrays = [pa.array(utc_times), pa.array(flags), pa.array(points)]
    new_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    timeseries = Timeseries(
        table=new_table, full_name=TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH
    )

    with pytest.raises(
        grpc.RpcError, match="timestamps in the segment are not increasing"
    ):
        session.write_timeseries_points(timeseries)


@pytest.mark.database
def test_read_empty_timeseries(session):
    """
    Check that reading empty time series (without any points) is correctly handled.
    """
    empty_time_series_key = 9
    start_time = datetime(2016, 1, 1)
    end_time = datetime(2025, 1, 1)

    reply_timeseries = session.read_timeseries_points(
        empty_time_series_key, start_time, end_time
    )

    assert reply_timeseries.arrow_table is not None
    assert reply_timeseries.arrow_table.num_rows == 0
    # This check is redundant, but it is good to have it.
    assert reply_timeseries.number_of_points == 0

    assert reply_timeseries.start_time is None
    assert reply_timeseries.end_time is None
    assert reply_timeseries.resolution == Timeseries.Resolution.BREAKPOINT
    assert reply_timeseries.timskey == empty_time_series_key


@pytest.mark.asyncio
@pytest.mark.database
async def test_timeseries_async(async_session):
    """For async run the simplest test, implementation is the same."""

    new_table = get_test_time_series_pyarrow_table()

    attribute_path = TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH

    await async_session.write_timeseries_points(
        Timeseries(table=new_table, full_name=attribute_path)
    )

    reply_timeseries = await async_session.read_timeseries_points(
        target=attribute_path,
        start_time=TIME_SERIES_START_TIME,
        end_time=TIME_SERIES_END_TIME,
    )

    assert new_table == reply_timeseries.arrow_table


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
