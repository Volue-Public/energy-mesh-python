import unittest
import asyncio
from volue import mesh
from volue.mesh import mesh_pb2

# Todo: Move this to a utils file or something
def await_if_async(coroutine):
    if (asyncio.iscoroutine(coroutine)):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coroutine)
    return coroutine


# These should be run with a mesh server
def impl_test_get_version(test, connection):
    version_info = await_if_async(connection.get_version())
    test.assertEqual(
        version_info.status.status_code, 
        mesh_pb2.Status.StatusCode.OK)
    # Verify that mesh returned something
    test.assertIsNot(
        version_info.full_version,
        "")


def impl_test_start_and_close_only_one_session(test, connection):
    # Test that we are able to start and end a session,
    # and that we are not allowed to start more than one session
    # at a time.

    # At this time, we don't have a session id yet
    test.assertIsNone(connection.session_id)
    
    session_reply_1 = await_if_async(connection.start_session())
    test.assertEqual(
        session_reply_1.status.status_code, 
        mesh_pb2.Status.StatusCode.OK)

    # Verify that we have a session id now = session started
    test.assertIsNotNone(connection.session_id)

    # Remember the session id.
    session_id_1 = connection.session_id

    # We already have a session, so we should not be allowed
    # to start another one:
    session_reply_2 = await_if_async(connection.start_session())

    # Should not be ok, we are not allowed to start another session
    # before we close the old one.
    test.assertNotEqual(
        session_reply_2.status.status_code, 
        mesh_pb2.Status.StatusCode.OK)

    session_id_2 = connection.session_id

    # The session ids should be the same
    test.assertEqual(session_id_1, session_id_2)


class SessionTests(unittest.TestCase):
    def test_get_version(self):
        impl_test_get_version(self, mesh.Connection())
        impl_test_get_version(self, mesh.AsyncConnection())

    def test_start_and_close_session(self):
        impl_test_start_and_close_only_one_session(self, mesh.Connection())
        impl_test_start_and_close_only_one_session(self, mesh.AsyncConnection())


if __name__ == '__main__':
    unittest.main()
