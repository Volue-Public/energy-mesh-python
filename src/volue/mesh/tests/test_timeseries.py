from volue.mesh import Connection, Timeserie, uuid_to_guid, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh.proto.mesh_pb2 import ObjectId, UtcInterval, WriteTimeseriesRequest
from volue.mesh.tests.test_utilities.server_config import ADDRESS, PORT, SECURE_CONNECTION
from volue.mesh.tests.test_utilities.utilities import await_if_async

from google.protobuf.timestamp_pb2 import Timestamp
import string
import unittest
import uuid
import grpc
import pyarrow
import pytest


def compare_segments(seg_1, seg_2):
    n_1 = seg_1.number_of_points
    n_2 = seg_2.number_of_points
    assert n_1 == n_2


# These should be run with a mesh server
def impl_test_get_and_edit_timeseries_points(
        connection,
        timskey: int = None,
        uuid: uuid.UUID = None,
        full_name: string = None):
    # 1. Start session
    # 2. Edit timeseries with random numbers
    # 3. Read timeseries, compare with step 2.
    session = connection.create_session()
    write_reply = await_if_async(session.open())
    assert write_reply is not None

    # Preapare the request
    # TODO: When possible, check for existence and create this timeseries
    start = dot_net_ticks_to_protobuf_timestamp(635976576000000000)
    end = dot_net_ticks_to_protobuf_timestamp(635987808000000000)
    interval = UtcInterval(
        start_time=start,
        end_time=end
    )

    read_reply_1 = await_if_async(
        session.read_timeseries_points(
            timskey=timskey,
            guid=uuid,
            full_name=full_name,
            interval=interval))

    # Send request
    try:
        await_if_async(
            session.write_timeseries_points(
                timskey=timskey,
                guid=uuid_to_guid(uuid),
                full_name=full_name,
                interval=interval,
                timeserie=next(Timeserie.read_timeseries_reply(read_reply_1))))
    except grpc.RpcError:
        pytest.fail("Could not write timeseries points")

    assert write_reply is not None

    try:
        await_if_async(session.commit())
    except grpc.RpcError:
        pytest.fail("Could not commit changes.")

    # Read the timeseries we just edited
    try:
        read_reply_2 = await_if_async(
            session.read_timeseries_points(
                timskey=timskey,
                guid=uuid,
                full_name=full_name,
                interval=interval))
    except grpc.RpcError:
        pytest.fail("Could not read timeseries points")
    finally:
        assert read_reply_2 is not None

    # Check that the values are the same as we just wrote
    assert len(read_reply_2.timeseries) > 0
    compare_segments(next(Timeserie.read_timeseries_reply(read_reply_1)),
                     next(Timeserie.read_timeseries_reply(read_reply_2))
                     )

    # Done! Close session.
    await_if_async(session.close())


@pytest.mark.unittest
def test_can_convert_between_win32ticks_and_timestamp():
    original_ts = Timestamp()
    original_ts.FromJsonString(value="2021-08-19T00:00:00Z")
    original_ticks = 637649280000000000  # "2021-08-19T00:00:00Z"
    ts = dot_net_ticks_to_protobuf_timestamp(original_ticks)
    assert original_ts.ToNanoseconds() == ts.ToNanoseconds()


@pytest.mark.unittest
def test_can_create_empty_timeserie():
    ts = Timeserie()
    assert ts is not None


@pytest.mark.unittest
def test_can_add_point_to_timeserie():
    ts = Timeserie()
    assert ts.number_of_points == 0
    ts.add_point(123, 123, 0.123)
    assert ts.number_of_points == 1
    ts.add_point(345, 345, 0.234)
    assert ts.number_of_points == 2


@pytest.mark.unittest
def test_can_serialize_and_deserialize_write_timeserie_request():
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

    timeserie_original = Timeserie()
    assert timeserie_original is not None
    timeserie_original.add_point(0, 0, 0.0)
    timeserie_original.add_point(1, 1, 1.0)
    timeserie_original.add_point(2, 2, 2.0)
    assert timeserie_original.number_of_points == 3

    proto_timeserie_original = timeserie_original.to_proto_timeseries(object_id_original, interval)
    session_id_original = uuid_to_guid(uuid.UUID("3f1afdd7-1111-45f9-824f-a7adc09cff8e"))

    request_original = WriteTimeseriesRequest(
        session_id=session_id_original,
        object_id=object_id_original,
        timeseries=proto_timeserie_original
    )

    binary_data = request_original.SerializeToString()
    assert binary_data is not None

    request = WriteTimeseriesRequest()

    request.ParseFromString(binary_data)
    assert request_original == request
    assert session_id_original == request.session_id
    assert object_id_original == request.object_id
    assert proto_timeserie_original == request.timeseries

    reader = pyarrow.ipc.open_stream(request.timeseries.data)
    table = reader.read_all()
    assert timeserie_original.arrow_table == table
    assert timeserie_original.arrow_table[0] == table[0]
    assert timeserie_original.arrow_table[1] == table[1]
    assert timeserie_original.arrow_table[2] == table[2]


@pytest.mark.database
def test_get_and_edit_timeseries_points_from_timskey():
    timskey = 201503
    impl_test_get_and_edit_timeseries_points(Connection(ADDRESS, PORT, SECURE_CONNECTION), timskey)
    impl_test_get_and_edit_timeseries_points(AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION), timskey)


@pytest.mark.database
def test_get_and_edit_timeseries_points_from_uuid():
    uuid_id = uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e")
    impl_test_get_and_edit_timeseries_points(Connection(ADDRESS, PORT, SECURE_CONNECTION), None, uuid_id)
    impl_test_get_and_edit_timeseries_points(AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION), None, uuid_id)


if __name__ == '__main__':
    unittest.main()
