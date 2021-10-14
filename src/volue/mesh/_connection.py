import datetime
import grpc
import uuid
from typing import Optional
from google import protobuf
from volue.mesh import Timeseries, guid_to_uuid, uuid_to_guid, Credentials, datetime_to_protobuf_utcinterval
from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc


class Connection:
    """ """

    class Session:
        """
        This class supports the with statement, because it's a contextmanager.
        """

        def __init__(self, mesh_service: mesh_pb2_grpc.MeshServiceStub, session_id: uuid = None):
            self.session_id: uuid = session_id
            self.mesh_service: mesh_pb2_grpc.MeshServiceStub = mesh_service

        def __enter__(self):
            """
            """
            self.open()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            """
            self.close()

        def open(self) -> None:
            """
            Raises:
                grpc.RpcError:

            """
            reply = self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = guid_to_uuid(reply.bytes_le)

        def close(self) -> None:
            """
            Raises:
                grpc.RpcError:
            """
            self.mesh_service.EndSession(uuid_to_guid(self.session_id))
            self.session_id = None

        def read_timeseries_points(self,
                                   start_time: datetime,
                                   end_time: datetime,
                                   timskey: int = None,
                                   guid: uuid.UUID = None,
                                   full_name: str = None) -> Timeseries:
            """
            Args:
                start_time:
                end_time:

            Raises:
                grpc.RpcError:
            """
            object_id = mesh_pb2.ObjectId(
                timskey=timskey,
                guid=uuid_to_guid(guid),
                full_name=full_name)

            reply = self.mesh_service.ReadTimeseries(
                mesh_pb2.ReadTimeseriesRequest(
                    session_id=uuid_to_guid(self.session_id),
                    object_id=object_id,
                    interval=datetime_to_protobuf_utcinterval(start_time, end_time)
                )
            )
            # TODO: This need to handle more than 1 timeserie
            return next(Timeseries._read_timeseries_reply(reply))

        def write_timeseries_points(
                self,
                start_time: datetime,
                end_time: datetime,
                timeserie: Timeseries,
                timskey: int = None,
                guid: uuid.UUID = None,
                full_name: str = None) -> None:
            """
            Raises:
                grpc.RpcError:
            """
            object_id = mesh_pb2.ObjectId(
                timskey=timskey,
                guid=uuid_to_guid(guid),
                full_name=full_name)

            proto_timeserie = timeserie.to_proto_timeseries(object_id=object_id, start_time=start_time, end_time=end_time)

            self.mesh_service.WriteTimeseries(
                mesh_pb2.WriteTimeseriesRequest(
                    session_id=uuid_to_guid(self.session_id),
                    object_id=object_id,
                    timeseries=proto_timeserie
                )
            )

        def rollback(self) -> None:
            """
            Raises:
                grpc.RpcError:
            """
            self.mesh_service.Rollback(uuid_to_guid(self.session_id))

        def commit(self) -> None:
            """
            Raises:
                grpc.RpcError:
            """
            self.mesh_service.Commit(uuid_to_guid(self.session_id))

    def __init__(self, host, port, secure_connection: bool):
        """
        """

        target = f'{host}:{port}'
        if not secure_connection:
            channel = grpc.insecure_channel(
                target=target
            )
        else:
            credentials: Credentials = Credentials()
            channel = grpc.secure_channel(
                target=target,
                credentials=credentials.channel_creds
            )

        self.mesh_service = mesh_pb2_grpc.MeshServiceStub(channel)

    def get_version(self):
        """
        """
        response = self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())
        return response

    def create_session(self) -> Optional[Session]:
        """
        Raises:
            grpc.RpcError:
        """
        return self.connect_to_session(session_id=None)

    def connect_to_session(self, session_id: uuid):
        """
        """
        return self.Session(self.mesh_service, session_id)
