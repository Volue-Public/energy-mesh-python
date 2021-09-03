import grpc
import uuid
from typing import Optional
from google import protobuf

from volue.mesh.timeserie import *
from volue.mesh.common import *
from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from volue.mesh.credentials import Credentials


class Connection:
    """Represents a connection to a mesh server.

    This class can be used to interact with the mesh grpc api.
    """

    def __init__(self, host: str = 'localhost', port: int = 50051, credentials: Credentials = Credentials()):
        """Connect to a running mesh server.

        Args:
            host (str): the server address
            port (int): servers gRPC port
            credentials (Credentials): securety details for the connection
        """

        if not hasattr(self, 'channel'):
            self.channel = grpc.secure_channel(
                target=f'{host}:{port}',
                credentials=credentials.channel_creds
            )
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)
        self.session_id = None


    def is_server_compatible(self) -> bool:
        """Checks if the connected mesh server version is compatible with this SDK version"""
        #TODO Fix
        return True


    def get_version(self) -> str:
        """Get the version of the mesh server that is connected.

        Returns:
            str: The version str for the connected mesh server.
        """

        try:
            response = self.stub.GetVersion(protobuf.empty_pb2.Empty())
        except grpc.RpcError as e:
            self.react_to_error(e)
        else:
            return response

    def start_session(self) -> Optional[mesh_pb2.Guid]:
        """Ask the server to start a session. Only one session can be active at any give connection.

        Returns:
            Optional[mesh_pb2.Guid]: The guid of the connected session or None if session could not be started.
        """

        if (self.session_id is None):
            try:
                reply = self.stub.StartSession(protobuf.empty_pb2.Empty())
            except grpc.RpcError as e:
                self.react_to_error(e)
            else:
                self.session_id = guid_to_uuid(reply.bytes_le)
                return reply
        return None

    def end_session(self) -> None:
        """Ask the server to end the session."""

        if self.session_id is not None:
            try:
                reply = self.stub.EndSession(uuid_to_guid(self.session_id))
            except grpc.RpcError as e:
                self.react_to_error(e)
            else:
                self.session_id = None
                return reply
        return None

    def read_timeseries_points(
            self,
            interval: mesh_pb2.UtcInterval,
            timskey: int = None,
            guid: uuid.UUID = None,
            full_name: str = None) -> Optional[mesh_pb2.ReadTimeseriesResponse]:
        """

        Args:
            interval (mesh_pb2.UtcInterval):
            timskey (int):
            guid (uuid.UUID):
            full_name (str):

        Returns:
            Optional[mesh_pb2.ReadTimeseriesResponse]:
        """

        object_id = mesh_pb2.ObjectId(
            timskey=timskey,
            guid=uuid_to_guid(guid),
            full_name=full_name)

        try:
            reply = self.stub.ReadTimeseries(
                mesh_pb2.ReadTimeseriesRequest(
                    session_id=uuid_to_guid(self.session_id),
                    object_id=object_id,
                    interval=interval
                )
            )
        except grpc.RpcError as e:
            self.react_to_error(e)
        else:
            return reply

    def write_timeseries_points(
            self,
            interval: mesh_pb2.UtcInterval,
            timeserie: Timeserie,
            timskey: int = None,
            guid: uuid.UUID = None,
            full_name: str = None) -> Optional[protobuf.empty_pb2.Empty]:
        """

        Args:
            interval (mesh_pb2.UtcInterval):
            timeserie (Timeserie):
            timskey (int):
            guid (uuid.UUID):
            full_name (str):

        Returns:

        """

        object_id = mesh_pb2.ObjectId(
            timskey=timskey,
            guid=uuid_to_guid(guid),
            full_name=full_name)

        proto_timeserie = timeserie.to_proto_timeseries(
            object_id=object_id,
            interval=interval
        )

        try:
            reply = self.stub.WriteTimeseries(
                mesh_pb2.WriteTimeseriesRequest(
                    session_id=uuid_to_guid(self.session_id),
                    object_id=object_id,
                    timeseries=proto_timeserie
                )
            )
        except grpc.RpcError as e:
            self.react_to_error(e)
        else:
            return reply
        return None

    def rollback(self):
        """

        Returns:

        """
        return self.stub.Rollback(uuid_to_guid(self.session_id))

    def commit(self):
        """

        Returns:

        """
        return self.stub.Commit(uuid_to_guid(self.session_id))

    def react_to_error(self, e: grpc.RpcError) -> None:
        """Prints errors received from the mesh gRPC API.

        Args:
            e (grpc.RpcError): The error thrown from

        """

        # TODO need more intelligent error handling
        print(f"""
            gRPC error:
                Details:        {e.details()}
                Status code:    {e.code()}
        """)
