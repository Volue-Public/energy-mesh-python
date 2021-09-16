import unittest

import grpc
import pytest

from volue import mesh
from tests.test_utilities.utilities import await_if_async
from tests.test_utilities.server_config import ADDRESS, PORT, SECURE_CONNECTION


def impl_test_get_version(test, connection):
    version_info = await_if_async(connection.get_version())
    test.assertIsNot(version_info.full_version, "")


def impl_test_start_and_close_only_one_session(test, connection):
    # Test that we are able to start and end a session,
    # and that we are not allowed to start more than one session
    # at a time.

    # At this time, we don't have a session id yet
    test.assertIsNone(connection.session_id)

    session_reply_1 = await_if_async(connection.start_session())

    # Verify that we have a session id now = session started
    test.assertIsNotNone(connection.session_id)

    # Remember the session id.
    session_id_1 = connection.session_id

    # We already have a session, so we should not be allowed
    # to start another one:
    with test.assertRaises(grpc.RpcError):
        await_if_async(connection.start_session())

    session_id_2 = connection.session_id

    # The session ids should be the same
    test.assertEqual(session_id_1, session_id_2)


class TestSession(unittest.TestCase):

    @pytest.mark.server
    def test_get_version(self):
        impl_test_get_version(self, mesh.Connection(ADDRESS, PORT, SECURE_CONNECTION))
        impl_test_get_version(self, mesh.AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION))

    @pytest.mark.server
    def test_start_and_close_session(self):
        impl_test_start_and_close_only_one_session(self, mesh.Connection(ADDRESS, PORT, SECURE_CONNECTION))
        impl_test_start_and_close_only_one_session(self, mesh.AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION))


if __name__ == '__main__':
    unittest.main()
