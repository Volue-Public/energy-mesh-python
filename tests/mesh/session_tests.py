import unittest
import uuid
from volue import mesh
from volue.mesh import check_result, mesh_pb2

# These should be run with a mesh server

class SessionTests(unittest.TestCase):

    def test_get_version(self):
        connection = mesh.Connection()
        version_info = connection.get_version()
        self.assertEqual(
            version_info.status.status_code, 
            mesh_pb2.Status.StatusCode.OK)
        # Verify that mesh returned something
        self.assertIsNot(
            version_info.full_version,
            "")

    def test_start_and_close_session(self):
        # Test that we are able to start and end
        # a session
        connection = mesh.Connection()
        # At this time, we don't have a session id yet
        self.assertIsNone(connection.session_id)
        
        session_reply = connection.start_session()
        self.assertEqual(
            session_reply.status.status_code, 
            mesh_pb2.Status.StatusCode.OK)
        # Verify that we have a session id
        self.assertIsNotNone(connection.session_id)

        connection.end_session()
        self.assertEqual(
            session_reply.status.status_code, 
            mesh_pb2.Status.StatusCode.OK)
        # and now we shouldn't any more.
        self.assertIsNone(connection.session_id)

    def test_start_only_one_session(self):
        connection = mesh.Connection()
        session_reply_1 = connection.start_session()
        self.assertEqual(
            session_reply_1.status.status_code, 
            mesh_pb2.Status.StatusCode.OK)
        
        # Remember the session id.
        session_id_1 = connection.session_id

        # We already have a session, so we should not be allowed
        # to start another one:
        session_reply_2 = connection.start_session()

        # Should not be ok, we are not allowed to start another session
        # before we close the old one.
        self.assertNotEqual(
            session_reply_2.status.status_code, 
            mesh_pb2.Status.StatusCode.OK)

        session_id_2 = connection.session_id

        # The session ids should be the same
        self.assertEqual(session_id_1, session_id_2)
        

if __name__ == '__main__':
    unittest.main()