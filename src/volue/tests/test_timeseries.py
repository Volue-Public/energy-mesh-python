import string
import unittest
import uuid

import grpc
import pyarrow
import pytest

from volue.mesh.connection import Connection
from volue.mesh.async_connection import AsyncConnection
from volue.mesh.timeserie import Timeserie
from volue.mesh.common import uuid_to_guid
from volue.mesh.proto.mesh_pb2 import ObjectId, UtcInterval, WriteTimeseriesRequest
from volue.mesh.common import dot_net_ticks_to_protobuf_timestamp
from volue.tests.test_utilities.server_config import ADDRESS, PORT, SECURE_CONNECTION

from volue.tests.test_utilities.utilities import await_if_async
from google.protobuf.timestamp_pb2 import Timestamp


def compare_segments(test, seg_1, seg_2):
    n_1 = seg_1.number_of_points
    n_2 = seg_2.number_of_points
    test.assertEqual(n_1, n_2)


# These should be run with a mesh server
def impl_test_get_and_edit_timeseries_points(
        test: unittest.TestCase,
        connection,
        timskey: int = None,
        uuid: uuid.UUID = None,
        full_name: string = None):
    # 1. Start session
    # 2. Edit timeseries with random numbers
    # 3. Read timeseries, compare with step 2.
    write_reply = await_if_async(connection.start_session())
    test.assertNotEqual(write_reply, None)

    # Preapare the request
    # TODO: When possible, check for existence and create this timeseries
    start = dot_net_ticks_to_protobuf_timestamp(635976576000000000)
    end = dot_net_ticks_to_protobuf_timestamp(635987808000000000)
    interval = UtcInterval(
        start_time=start,
        end_time=end
    )

    read_reply_1 = await_if_async(
        connection.read_timeseries_points(
            timskey=timskey,
            guid=uuid,
            full_name=full_name,
            interval=interval))

    # Send request
    try:
        await_if_async(
            connection.write_timeseries_points(
                timskey=timskey,
                guid=uuid_to_guid(uuid),
                full_name=full_name,
                interval=interval,
                timeserie=next(Timeserie.read_timeseries_reply(read_reply_1))))
    except grpc.RpcError:
        test.fail("Could not write timeseries points")

    test.assertNotEqual(write_reply, None)

    try:
        await_if_async(connection.commit())
    except grpc.RpcError:
        test.fail("Could not commit changes.")

    # Read the timeseries we just edited
    try:
        read_reply_2 = await_if_async(
            connection.read_timeseries_points(
                timskey=timskey,
                guid=uuid,
                full_name=full_name,
                interval=interval))
    except grpc.RpcError:
        test.fail("Could not read timeseries points")
    finally:
        test.assertNotEqual(read_reply_2, None)

    # Check that the values are the same as we just wrote
    test.assertGreater(len(read_reply_2.timeseries), 0)
    compare_segments(test,
                     next(Timeserie.read_timeseries_reply(read_reply_1)),
                     next(Timeserie.read_timeseries_reply(read_reply_2))
                     )

    # Done! Close session.
    await_if_async(connection.end_session())


class TestTimeseries(unittest.TestCase):

    @pytest.mark.unittest
    def test_can_convert_between_win32ticks_and_timestamp(self):
        original_ts = Timestamp()
        original_ts.FromJsonString(value="2021-08-19T00:00:00Z")
        original_ticks = 637649280000000000  # "2021-08-19T00:00:00Z"
        ts = dot_net_ticks_to_protobuf_timestamp(original_ticks)
        self.assertEqual(original_ts.ToNanoseconds(), ts.ToNanoseconds())

    @pytest.mark.unittest
    def test_can_create_empty_timeserie(self):
        ts = Timeserie()
        self.assertNotEqual(ts, None)

    @pytest.mark.unittest
    def test_can_add_point_to_timeserie(self):
        ts = Timeserie()
        self.assertEqual(ts.number_of_points, 0)
        ts.add_point(123, 123, 0.123)
        self.assertEqual(ts.number_of_points, 1)
        ts.add_point(345, 345, 0.234)
        self.assertEqual(ts.number_of_points, 2)

    @pytest.mark.unittest
    def test_can_serialize_and_deserialize_write_timeserie_request(self):
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
        self.assertIsNotNone(timeserie_original)
        timeserie_original.add_point(0, 0, 0.0)
        timeserie_original.add_point(1, 1, 1.0)
        timeserie_original.add_point(2, 2, 2.0)
        self.assertEqual(timeserie_original.number_of_points, 3)

        proto_timeserie_original = timeserie_original.to_proto_timeseries(object_id_original, interval)
        session_id_original = uuid_to_guid(uuid.UUID("3f1afdd7-1111-45f9-824f-a7adc09cff8e"))

        request_original = WriteTimeseriesRequest(
            session_id=session_id_original,
            object_id=object_id_original,
            timeseries=proto_timeserie_original
        )

        binary_data = request_original.SerializeToString()
        self.assertIsNotNone(binary_data)

        request = WriteTimeseriesRequest()

        request.ParseFromString(binary_data)
        self.assertEqual(request_original, request)
        self.assertEqual(session_id_original, request.session_id)
        self.assertEqual(object_id_original, request.object_id)
        self.assertEqual(proto_timeserie_original, request.timeseries)

        reader = pyarrow.ipc.open_stream(request.timeseries.data)
        table = reader.read_all()
        self.assertEqual(timeserie_original.arrow_table, table)
        self.assertEqual(timeserie_original.arrow_table[0], table[0])
        self.assertEqual(timeserie_original.arrow_table[1], table[1])
        self.assertEqual(timeserie_original.arrow_table[2], table[2])

    @pytest.mark.database
    def test_get_and_edit_timeseries_points_from_timskey(self):
        timskey = 201503
        impl_test_get_and_edit_timeseries_points(self, Connection(ADDRESS, PORT, SECURE_CONNECTION), timskey)
        impl_test_get_and_edit_timeseries_points(self, AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION), timskey)

    @pytest.mark.database
    def test_get_and_edit_timeseries_points_from_uuid(self):
        uuid_id = uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e")
        impl_test_get_and_edit_timeseries_points(self, Connection(ADDRESS, PORT, SECURE_CONNECTION), None, uuid_id)
        impl_test_get_and_edit_timeseries_points(self, AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION), None,
                                                 uuid_id)

    # TODO next level??
    # def test_get_and_edit_timeseries_points_from_search_string(self):
    #     search_string = "/TEK/Windpark/Valsneset/.Vals_WindDir_forecast"
    #     impl_test_get_and_edit_timeseries_points(self, mesh.Connection(ADDRESS, PORT, SECURE_CONNECTION), search_string=search_string)
    #     impl_test_get_and_edit_timeseries_points(self, mesh.AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION), search_string=search_string)


if __name__ == '__main__':
    unittest.main()