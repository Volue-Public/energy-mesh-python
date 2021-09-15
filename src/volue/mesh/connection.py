import grpc
import uuid
from typing import Optional
from google import protobuf

from volue.mesh.timeserie import Timeserie
from volue.mesh.common import guid_to_uuid, uuid_to_guid
from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from volue.mesh.credentials import Credentials


class Connection:
    """Represents a connection to a mesh server.

    This class can be used to interact with the mesh grpc api.
    """

    def __init__(self, host: str, port: int, secure_connection: bool):
        """Connect to a running mesh server.

        Args:
            host (str): the server address
            port (int): servers gRPC port
            secure_connection (bool): establish connection using TLS
        """

        if not hasattr(self, 'channel'):
            target = f'{host}:{port}'
            if not secure_connection:
                self.channel = grpc.insecure_channel(
                    target=target
                )
            else:
                credentials: Credentials = Credentials()
                self.channel = grpc.secure_channel(
                    target=target,
                    credentials=credentials.channel_creds
                )
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)
        self.session_id = None

    def is_server_compatible(self) -> bool:
        """Checks if the connected mesh server version is compatible with this SDK version"""
        # TODO Fix
        return True

    def get_version(self) -> str:
        """Get the version of the mesh server that is connected.

        Raises:
            grpc.RpcError:

        Returns:
            str: The version str for the connected mesh server.
        """
        return self.stub.GetVersion(protobuf.empty_pb2.Empty())

    def start_session(self) -> uuid.UUID:
        """Ask the server to start a session. Only one session can be active at any give connection.

        Raises:
            grpc.RpcError:

        Returns:
            Optional[mesh_pb2.Guid]: The guid of the connected session or None if session could not be started.
        """
        reply = self.stub.StartSession(protobuf.empty_pb2.Empty())
        self.session_id = guid_to_uuid(reply.bytes_le)

        return self.session_id

    def end_session(self) -> None:
        """Ask the server to end the session.

        Raises:
            grpc.RpcError:
        """
        self.stub.EndSession(uuid_to_guid(self.session_id))
        self.session_id = None

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

        Raises:
            grpc.RpcError:

        Returns:
            Optional[mesh_pb2.ReadTimeseriesResponse]:
        """
        object_id = mesh_pb2.ObjectId(
            timskey=timskey,
            guid=uuid_to_guid(guid),
            full_name=full_name)

        reply = self.stub.ReadTimeseries(
            mesh_pb2.ReadTimeseriesRequest(
                session_id=uuid_to_guid(self.session_id),
                object_id=object_id,
                interval=interval
            )
        )
        return reply

    def write_timeseries_points(
            self,
            interval: mesh_pb2.UtcInterval,
            timeserie: Timeserie,
            timskey: int = None,
            guid: uuid.UUID = None,
            full_name: str = None) -> None:
        """

        Args:
            interval (mesh_pb2.UtcInterval):
            timeserie (Timeserie):
            timskey (int):
            guid (uuid.UUID):
            full_name (str):

        Raises:
            grpc.RpcError:

        """
        object_id = mesh_pb2.ObjectId(
            timskey=timskey,
            guid=uuid_to_guid(guid),
            full_name=full_name)

        proto_timeserie = timeserie.to_proto_timeseries(
            object_id=object_id,
            interval=interval
        )

        self.stub.WriteTimeseries(
            mesh_pb2.WriteTimeseriesRequest(
                session_id=uuid_to_guid(self.session_id),
                object_id=object_id,
                timeseries=proto_timeserie
            )
        )

    def rollback(self) -> None:
        """ Roll back changes.

        Raises:
            grpc.RpcError:
        """
        self.stub.Rollback(uuid_to_guid(self.session_id))

    def commit(self) -> None:
        """ Commit changes.

        Raises:
            grpc.RpcError:
        """
        self.stub.Commit(uuid_to_guid(self.session_id))
