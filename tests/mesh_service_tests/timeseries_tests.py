import unittest
import asyncio
import random
import uuid
import string

from volue import mesh
from volue.mesh import mesh_pb2


# TODO: Move this to a utils file or something
# Helper function to allow us to use same test for async and sync connection
def await_if_async(coroutine):
    if (asyncio.iscoroutine(coroutine)):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coroutine)
    return coroutine


def create_timeseries_segment(start_time, end_time, delta_t) -> mesh_pb2.TimeseriesSegment:
    t = start_time
    segment = mesh_pb2.TimeseriesSegment()
    while (t < end_time):
        point = segment.points.add()
        point.value = random.randint(-10000, 10000)
        point.timestamp = t
        t += delta_t
    return segment


def compare_points(test, point_1, point_2):
    ts_1 = point_1.timestamp
    ts_2 = point_2.timestamp
    test.assertEqual(ts_1, ts_2)

    value_1 = point_1.value
    value_2 = point_2.value
    test.assertEqual(value_1, value_2)

    flags_1 = point_1.flags
    flags_2 = point_2.flags
    test.assertEqual(flags_1, flags_2)
    

def compare_segments(test, seg_1, seg_2):
    n_1 = len(seg_1.points)
    n_2 = len(seg_2.points)
    test.assertEqual(n_1, n_2)
    i = 0
    while (i < n_1):
        point_1 = seg_1.points[i]
        point_2 = seg_2.points[i]
        compare_points(test, point_1, point_2)
        i += 1


# These should be run with a mesh server
def impl_test_get_and_edit_timeseries_points(
    test: unittest.TestCase, 
    connection,
    timskey: int = None,
    entry_id: uuid.UUID = None,
    search_string: string = None):
    # 1. Start session
    # 2. Edit timeseries with random numbers
    # 3. Read timeseries, compare with step 2.
    reply = await_if_async(connection.start_session())
    test.assertEqual(
        reply.status.status_code, 
        mesh_pb2.Status.StatusCode.OK)

    # Preapare the request
    # TODO: When possible, check for existence and create this timeseries
    interval = mesh_pb2.UtcInterval(
        start_time=637450560000000000, end_time=637451424000000000
    )

    # Create timeseries with hourly resolution
    segment = create_timeseries_segment(interval.start_time, interval.end_time, 36000000000)

    # Send request, and wait for reply
    reply = await_if_async(
        connection.edit_timeseries_points(
            timskey=timskey,
            entry_id=entry_id,
            search_string=search_string,
            interval=interval,
            points=segment))

    test.assertEqual(
        reply.status.status_code, 
        mesh_pb2.Status.StatusCode.OK)

    reply = await_if_async(connection.commit())
    
    test.assertEqual(
        reply.status.status_code, 
        mesh_pb2.Status.StatusCode.OK)

    # Read the timeseries we just edited
    reply = await_if_async(
        connection.get_timeseries_points(
            timskey=timskey,
            entry_id=entry_id,
            search_string=search_string,
            interval=interval))

    test.assertEqual(
        reply.status.status_code, 
        mesh_pb2.Status.StatusCode.OK)

    # Check that the values are the same as we just wrote
    test.assertGreater(len(reply.segments), 0)

    compare_segments(test, segment, reply.segments[0])

    # Done! Close session.
    await_if_async(connection.end_session())


class SessionTests(unittest.TestCase):
    def test_get_and_edit_timeseries_points_from_timskey(self):
        timskey = 2125
        impl_test_get_and_edit_timeseries_points(self, mesh.Connection(), timskey)
        impl_test_get_and_edit_timeseries_points(self, mesh.AsyncConnection(), timskey)
    
    def test_get_and_edit_timeseries_points_from_entry_id(self):
        entry_id = uuid.UUID("3F639110-D1D5-440C-A3D1-09E75D333DFF")
        impl_test_get_and_edit_timeseries_points(self, mesh.Connection(), None, entry_id)
        impl_test_get_and_edit_timeseries_points(self, mesh.AsyncConnection(), None, entry_id)

    # def test_get_and_edit_timeseries_points_from_search_string(self):
    #     search_string = "/TEK/Windpark/Valsneset/.Vals_WindDir_forecast"
    #     impl_test_get_and_edit_timeseries_points(self, mesh.Connection(), search_string=search_string)
    #     impl_test_get_and_edit_timeseries_points(self, mesh.AsyncConnection(), search_string=search_string)

if __name__ == '__main__':
    unittest.main()
