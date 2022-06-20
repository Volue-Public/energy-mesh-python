"""
Tests for volue.mesh.Timeseries
"""

from datetime import datetime, timedelta
import uuid

import pyarrow as pa
import pytest

from volue.mesh import Timeseries
from volue.mesh._common import _to_proto_timeseries, _to_proto_guid
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.proto.type import resources_pb2


@pytest.mark.unittest
def test_can_create_empty_timeserie():
    """Check that an empty time series can be created."""
    ts = Timeseries()
    assert ts is not None


@pytest.mark.unittest
def test_can_create_timeserie_from_existing_data():
    """Check that a time series can be created from existing data."""

    arrays = [
        pa.array([datetime(2016, 5, 1), datetime(2016, 5, 1, 1), datetime(2016, 5, 1, 2)], type=pa.timestamp('ms')),
        pa.array([0, 0, 0], type=pa.uint32()),
        pa.array([0.0, 0.0, 0.0])]
    table = pa.Table.from_arrays(arrays=arrays, names=["utc_time", "flags", "value"])
    time_series = Timeseries(table)
    assert time_series.number_of_points == 3


@pytest.mark.unittest
def test_init_timeseries_with_wrong_pyarrow_table_schema_should_throw():
    """Check that a time series can't be created with invalid PyArrow table schema."""

    arrays = [pa.array(['one', 'two', 'three', 'four', 'five']),
              pa.array([1, 2, 3, 4, 5]),
              pa.array([6, 7, 8, 9, 10])]

    table = pa.Table.from_arrays(arrays=arrays, names=["name", "first_list", "second_list"])
    with pytest.raises(TypeError, match="invalid PyArrow table schema"):
        Timeseries(table)

    # schema names are correct, but types not - still should be an error
    table = pa.Table.from_arrays(arrays=arrays, names=["utc_time", "flags", "value"])
    with pytest.raises(TypeError, match="invalid PyArrow table schema"):
        Timeseries(table)


@pytest.mark.unittest
def test_can_serialize_and_deserialize_write_timeserie_request():
    """Check that timeseries can be de-/serialized."""

    start = datetime(year=2013, month=7, day=25, hour=0, minute=0, second=0)  # 25/07/2013 00:00:00
    end = datetime(year=2016, month=12, day=25, hour=0, minute=0, second=0)  # 25/12/2016 00:00:00

    arrays = [
        pa.array([datetime(2016, 5, 1), datetime(2016, 5, 1, 1), datetime(2016, 5, 1, 2)]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 0.0, 0.0])]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    original_timeseries = Timeseries(table=table,
                                     resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
                                     start_time=start, end_time=end,
                                     timskey=1,
                                     uuid_id=uuid.uuid4(),
                                     full_name="some_name")

    assert original_timeseries.start_time == start
    assert original_timeseries.end_time == end

    original_proto_timeseries = _to_proto_timeseries(original_timeseries)
    session_id_original = _to_proto_guid(uuid.uuid4())

    original_reply = core_pb2.WriteTimeseriesRequest(
        session_id=session_id_original,
        timeseries=original_proto_timeseries
    )

    binary_data = original_reply.SerializeToString()
    assert binary_data is not None

    reply = core_pb2.WriteTimeseriesRequest()
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
        pa.array([datetime(2016, 5, 1), datetime(2016, 5, 1, 1), datetime(2016, 5, 1, 2)]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 0.0, 0.0])]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    time_series = Timeseries(table=table,
                             resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
                             timskey=1,
                             uuid_id=uuid.uuid4(),
                             full_name="some_name")
    assert time_series.start_time == datetime(2016, 5, 1)
    assert time_series.end_time == datetime(2016, 5, 1, 2) + timedelta(seconds=1)


@pytest.mark.unittest
def test_timeseries_without_explicit_start_end_datetime_and_pyarrow_table():
    """
    Check that a time series can be created without providing
    explicitly `start_time`, `end_time` and PyArrow `table` arguments.
    """

    time_series = Timeseries(resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
                             timskey=1,
                             uuid_id=uuid.uuid4(),
                             full_name="some_name")
    assert time_series.number_of_points == 0


@pytest.mark.unittest
def test_timeseries_without_explicit_start_end_datetime_and_empty_pyarrow_table():
    """
    Check that a time series can be created without providing
    explicitly `start_time`, `end_time` and PyArrow `table` arguments.
    """

    arrays = [
        pa.array([]),
        pa.array([]),
        pa.array([])]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    time_series = Timeseries(table=table,
                             resolution=resources_pb2.Resolution(type=resources_pb2.Resolution.HOUR),
                             timskey=1,
                             uuid_id=uuid.uuid4(),
                             full_name="some_name")
    assert time_series.number_of_points == 0

if __name__ == '__main__':
    pytest.main()
