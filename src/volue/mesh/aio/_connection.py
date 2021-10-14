import grpc
import uuid
from google import protobuf
from typing import Optional
from volue.mesh import Timeseries, guid_to_uuid, uuid_to_guid, Credentials
from volue.mesh.proto import mesh_pb2, mesh_pb2_grpc


class Connection:
    """ """

    class Session:
        """
        This class supports the async with statement, because it's a async contextmanager.
        https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers
        https://docs.python.org/3/reference/compound_stmts.html#async-with
        """

        def __init__(self, mesh_service):
            self.session_id = None
            self.mesh_service = mesh_service

        async def __aenter__(self):
            """
            |coro|
            """
            await self.open()
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            """
            |coro|
            """
            await self.close()

        async def open(self):
            """
            |coro|

            Raises:
                grpc.RpcError:

            """
            reply = await self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = guid_to_uuid(reply.bytes_le)
            return reply

        async def close(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.EndSession(uuid_to_guid(self.session_id))
            self.session_id = None

        async def read_timeseries_points(
                self,
                interval: mesh_pb2.UtcInterval,
                timskey: int = None,
                guid: uuid.UUID = None,
                full_name: str = None):
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            object_id = mesh_pb2.ObjectId(
                timskey=timskey,
                guid=uuid_to_guid(guid),
                full_name=full_name)

            reply = await self.mesh_service.ReadTimeseries(
                mesh_pb2.ReadTimeseriesRequest(
                    session_id=uuid_to_guid(self.session_id),
                    object_id=object_id,
                    interval=interval
                )
            )
            # TODO: This need to handle more than 1 timeserie
            return next(Timeseries._read_timeseries_reply(reply))


        async def write_timeseries_points(
                self,
                interval: mesh_pb2.UtcInterval,
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

            proto_timeserie = timeserie.to_proto_timeseries(
                object_id=object_id,
                interval=interval
            )

            self.mesh_service.WriteTimeseries(
                mesh_pb2.WriteTimeseriesRequest(
                    session_id=uuid_to_guid(self.session_id),
                    object_id=object_id,
                    timeseries=proto_timeserie
                )
            )

        async def rollback(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.Rollback(uuid_to_guid(self.session_id))

        async def commit(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.Commit(uuid_to_guid(self.session_id))

    def __init__(self, host, port, secure_connection: bool):
        """
        """

        target = f'{host}:{port}'
        if not secure_connection:
            channel = grpc.aio.insecure_channel(
                target=target
            )
        else:
            credentials: Credentials = Credentials()
            channel = grpc.aio.secure_channel(
                target=target,
                credentials=credentials.channel_creds
            )

        self.mesh_service = mesh_pb2_grpc.MeshServiceStub(channel)

    async def get_version(self):
        """
        |coro|
        """
        response = await self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())
        return response

    def create_session(self) -> Optional[Session]:
        """
        Raises:
            grpc.RpcError:
        """
        # TODO  save it somewhere...?
        return self.Session(self.mesh_service)

    def delete_session(self) -> None:
        """
        Raises:
            grpc.RpcError:
        """
        # TODO how about it gets autodeleted as soon as an EVENT says the session is closed?
