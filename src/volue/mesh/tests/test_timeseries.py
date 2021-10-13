import uuid
import grpc
import pyarrow as pa
import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from volue.mesh import Connection, Timeseries, uuid_to_guid, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh.proto.mesh_pb2 import ObjectId, UtcInterval, WriteTimeseriesRequest
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
def test_can_create_empty_timeserie():
    """Check that an empty timeserie can be created."""
    ts = Timeseries()
    assert ts is not None


@pytest.mark.unittest
def test_can_create_timeserie_from_existing_data():
    """Check that a timeserie can be created from existing data."""
    arrays = [pa.array(['one', 'two', 'three', 'four', 'five']), pa.array([1, 2, 3, 4, 5]), pa.array([6, 7, 8, 9, 10])]
    table = pa.Table.from_arrays(arrays, names=["name", "first_list", "second_list"])
    ts = Timeseries(table)
    assert ts.number_of_points is 5


@pytest.mark.unittest
def test_can_serialize_and_deserialize_write_timeserie_request():
    """Check that timeseries can be de-/serialized."""
    object_id_original = ObjectId(
        timskey=201503,
        guid=uuid_to_guid(uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e")),
        full_name="Resource/Wind Power/WindPower/WPModel/WindProdForec(0)"
    )

    ts_start = Timestamp(seconds=1)
    ts_end = Timestamp(seconds=2)
    interval = UtcInterval(
        start_time=ts_start,
        end_time=ts_end
    )

    arrays = [
        pa.array([1462060800, 1462064400, 1462068000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 0.0, 0.0])]

    # TODO that way of getting the schema is not good... fix!
    table = pa.Table.from_arrays(arrays, schema=Timeseries().arrow_table.schema)
    timeserie_original = Timeseries(table)
    assert timeserie_original is not None

    proto_timeserie_original = timeserie_original.to_proto_timeseries(object_id_original, interval)
    session_id_original = uuid_to_guid(uuid.UUID("3f1afdd7-1111-45f9-824f-a7adc09cff8e"))

    request_original = WriteTimeseriesRequest(
        session_id=session_id_original,
        object_id=object_id_original,
        timeseries=proto_timeserie_original
    )

    binary_data = request_original.SerializeToString()
    assert binary_data is not None
    print(binary_data)

    request = WriteTimeseriesRequest()

    request.ParseFromString(binary_data)
    assert request_original == request
    assert session_id_original == request.session_id
    assert object_id_original == request.object_id
    assert proto_timeserie_original == request.timeseries

    reader = pa.ipc.open_stream(request.timeseries.data)
    table = reader.read_all()
    assert timeserie_original.arrow_table == table
    assert timeserie_original.arrow_table[0] == table[0]
    assert timeserie_original.arrow_table[1] == table[1]
    assert timeserie_original.arrow_table[2] == table[2]


@pytest.mark.database
def test_read_timeseries_points_using_timskey():
    """Check that timeseries can be retrieved using timskey."""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    with connection.create_session() as session:

        timeseries = session.read_timeseries_points(
                timskey=201503,
                interval=UtcInterval(
                    start_time=dot_net_ticks_to_protobuf_timestamp(635976576000000000),
                    end_time=dot_net_ticks_to_protobuf_timestamp(635987808000000000))
        )
        assert timeseries.number_of_points == 312


@pytest.mark.database
def test_get_and_edit_timeseries_points_from_timskey():
    """Check that a timeserie can be retrieved and editet using timskey."""
    timskey = 201503

    # Start session
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    session = connection.create_session()
    try:
        session.open()
    except grpc.RpcError:
        pytest.fail("Could not open session.")

    # Preapare the request
    start = dot_net_ticks_to_protobuf_timestamp(635976576000000000)
    end = dot_net_ticks_to_protobuf_timestamp(635987808000000000)
    interval = UtcInterval(
        start_time=start,
        end_time=end
    )

    timeseries = session.read_timeseries_points(
            timskey=timskey,
            interval=interval)

    # Send
    try:
        session.write_timeseries_points(
            timskey=timskey,
            interval=interval,
            timeserie=timeseries
        )
    except grpc.RpcError:
        pytest.fail("Could not write timeseries points")

    try:
        session.commit()
    except grpc.RpcError:
        pytest.fail("Could not commit changes.")

    # Read the timeseries we just edited
    try:
        timeseries2 = session.read_timeseries_points(
                timskey=timskey,
                interval=interval)
    except grpc.RpcError:
        pytest.fail("Could not read timeseries points")
    finally:
        assert timeseries2 is not None

    # Check that the values are the same as we just wrote
    assert timeseries2.number_of_points == 312
    assert timeseries.number_of_points == timeseries2.number_of_points

    # Done! Close session.
    try:
        session.close()
    except grpc.RpcError:
        pytest.fail("Could not close session")


@pytest.mark.asyncio
@pytest.mark.database
def test_get_and_edit_timeseries_points_from_timskey_async():
    timskey = 201503
    # impl_test_get_and_edit_timeseries_points(AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,sc.DefaultServerConfig.SECURE_CONNECTION), timskey)


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
