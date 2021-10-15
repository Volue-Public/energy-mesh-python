import uuid
import grpc
import pyarrow as pa
import pytest
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from volue.mesh import Connection, Timeseries, uuid_to_guid, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh.proto import mesh_pb2
from volue.mesh.proto.mesh_pb2 import WriteTimeseriesRequest
import volue.mesh.tests.test_utilities.server_config as sc


@pytest.mark.unittest
def test_can_convert_between_win32ticks_and_timestamp():
    """Check that conversion between win32ticks and timestamp works."""
    original_ts = Timestamp()
    original_ts.FromJsonString(value="2021-08-19T00:00:00Z")
    original_ticks = 637649280000000000  # "2021-08-19T00:00:00Z"
    ts = dot_net_ticks_to_protobuf_timestamp(original_ticks)
    assert original_ts.ToNanoseconds() == ts.ToNanoseconds()


@pytest.mark.unittest
def test_can_convert_between_datetime_and_timestamp():
    """Check that conversion between datetime and protobuf.timestamp works"""
    ts = Timestamp()
    ts.FromDatetime(datetime(2016, 5, 1))
    converted_ts = dot_net_ticks_to_protobuf_timestamp(635976576000000000)
    assert ts.ToNanoseconds() == converted_ts.ToNanoseconds()


@pytest.mark.unittest
def test_can_create_empty_timeserie():
    """Check that an empty timeserie can be created."""
    ts = Timeseries()
    assert ts is not None


@pytest.mark.unittest
def test_can_create_timeserie_from_existing_data():
    """Check that a timeserie can be created from existing data."""
    arrays = [pa.array(['one', 'two', 'three', 'four', 'five']), pa.array([1, 2, 3, 4, 5]), pa.array([6, 7, 8, 9, 10])]
    table = pa.Table.from_arrays(arrays, names=["name", "first_list", "second_list"])
    ts = Timeseries([table])
    assert ts.number_of_points == [5]


@pytest.mark.unittest
def test_can_serialize_and_deserialize_write_timeserie_request():
    """Check that timeseries can be de-/serialized."""

    start = datetime(year=2013, month=7, day=25, hour=0, minute=0, second=0)  # 25/07/2013 00:00:00
    end = datetime(year=2016, month=12, day=25, hour=0, minute=0, second=0)  # 25/12/2016 00:00:00

    arrays = [
        pa.array([1462060800, 1462064400, 1462068000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 0.0, 0.0])]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    original_timeseries = Timeseries(tables=[table],
                                    resolution=mesh_pb2.Resolution(type=mesh_pb2.Resolution.HOUR),
                                    start_time=start, end_time=end,
                                    timskey=201503,
                                    the_uuid=uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e"),
                                    full_name="Resource/Wind Power/WindPower/WPModel/WindProdForec(0)")

    original_proto_timeserie = original_timeseries.to_proto_timeseries()[0]
    session_id_original = uuid_to_guid(uuid.UUID("3f1afdd7-1111-45f9-824f-a7adc09cff8e"))

    original_reply = WriteTimeseriesRequest(
        session_id=session_id_original,
        object_id=original_timeseries.to_proto_object_id(),
        timeseries=original_proto_timeserie
    )

    binary_data = original_reply.SerializeToString()
    assert binary_data is not None

    reply = WriteTimeseriesRequest()
    reply.ParseFromString(binary_data)
    assert original_reply == reply
    assert session_id_original == reply.session_id
    assert original_timeseries.to_proto_object_id() == reply.object_id
    assert original_proto_timeserie == reply.timeseries

    reader = pa.ipc.open_stream(reply.timeseries.data)
    table = reader.read_all()
    assert original_timeseries.arrow_tables[0] == table
    assert original_timeseries.arrow_tables[0][0] == table[0]
    assert original_timeseries.arrow_tables[0][1] == table[1]
    assert original_timeseries.arrow_tables[0][2] == table[2]


@pytest.mark.database
def test_read_timeseries_points_using_timskey():
    """Check that timeseries can be retrieved using timskey."""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)
    with connection.create_session() as session:

        try:
            timeseries = session.read_timeseries_points(
                start_time=datetime(2016, 5, 1),
                end_time=datetime(2016, 5, 14),
                timskey=201503)
            assert timeseries.number_of_points == [312]
        except grpc.RpcError:
            pytest.fail("Could not read timeseries points")


@pytest.mark.database
def test_write_timeseries_points_using_timskey():
    """Check that timeseries can be written to the server using timskey."""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)
    arrays = [
        pa.array([1462060800, 1462064400, 1462068000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    timskey = 201503
    start_time = datetime(2016, 5, 1)
    end_time = datetime(2016, 5, 14)
    timeseries = Timeseries(tables=[table], start_time=start_time, end_time=end_time, timskey=timskey)

    with connection.create_session() as session:
        try:
            session.write_timeseries_points(
                timeserie=timeseries
            )
        except grpc.RpcError:
            pytest.fail("Could not write timeseries points")


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_and_edit_timeseries_points_from_timskey_async():

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)
    arrays = [
        pa.array([1462060800, 1462064400, 1462068000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    timskey = 201503
    start_time = datetime(2016, 5, 1)
    end_time = datetime(2016, 5, 14)
    timeseries = Timeseries(tables=[table], start_time=start_time, end_time=end_time, timskey=timskey)

    async with connection.create_session() as session:
        try:
            await session.write_timeseries_points(
                timeserie=timeseries
            )
        except grpc.RpcError:
            pytest.fail("Could not write timeseries points")


@pytest.mark.database
def test_get_and_edit_timeseries_points_from_uuid():
    """Check that a timeserie can be retreived using UUID."""
    uuid_id = uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e")
    # impl_test_get_and_edit_timeseries_points(Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION), None, uuid_id)


@pytest.mark.asyncio
@pytest.mark.database
def test_get_and_edit_timeseries_points_from_uuid_async():
    uuid_id = uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e")
    # impl_test_get_and_edit_timeseries_points(AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION), None, uuid_id)


if __name__ == '__main__':
    pytest.main()
