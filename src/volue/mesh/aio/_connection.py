from volue.mesh._common import *
from volue.mesh import Authentication, Timeseries, from_proto_guid, to_proto_guid, Credentials, to_protobuf_utcinterval
from volue.mesh.proto import mesh_pb2, mesh_pb2_grpc
from google import protobuf
from typing import Optional
from datetime import datetime
import grpc
import uuid


class Connection:
    """ """

    class Session:
        """
        This class supports the async with statement, because it's a async contextmanager.
        https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers
        https://docs.python.org/3/reference/compound_stmts.html#async-with
        """

        def __init__(
            self,
            mesh_service: mesh_pb2_grpc.MeshServiceStub,
            session_id: uuid = None,
            auth: Authentication = None,
            grpc_metadata: tuple = ()):
            """

            Args:
                mesh_service:
                session_id:
                auth:
                grpc_metadata:
            """
            self.session_id: uuid = session_id
            self.mesh_service: mesh_pb2_grpc.MeshServiceStub = mesh_service
            self.auth = auth
            self.grpc_metadata = grpc_metadata

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

        @Authentication.check_token_for_renewal
        async def open(self):
            """
            |coro|

            Raises:
                grpc.RpcError:

            """
            reply = await self.mesh_service.StartSession(protobuf.empty_pb2.Empty(),
                metadata = self.grpc_metadata)
            self.session_id = from_proto_guid(reply)
            return reply

        @Authentication.check_token_for_renewal
        async def close(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.EndSession(to_proto_guid(self.session_id),
                metadata = self.grpc_metadata)
            self.session_id = None

        @Authentication.check_token_for_renewal
        async def read_timeseries_points(
                self,
                start_time: datetime,
                end_time: datetime,
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
                guid=to_proto_guid(guid),
                full_name=full_name)

            reply = await self.mesh_service.ReadTimeseries(
                mesh_pb2.ReadTimeseriesRequest(
                    session_id=to_proto_guid(self.session_id),
                    object_id=object_id,
                    interval=to_protobuf_utcinterval(start_time, end_time)
                ),
                metadata = self.grpc_metadata
            )
            return read_proto_reply(reply)


        @Authentication.check_token_for_renewal
        async def write_timeseries_points(self, timeserie: Timeseries) -> None:
            """
            |coro|
            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.WriteTimeseries(
                mesh_pb2.WriteTimeseriesRequest(
                    session_id=to_proto_guid(self.session_id),
                    object_id=to_proto_object_id(timeserie),
                    timeseries=to_proto_timeseries(timeserie)
                ),
                metadata = self.grpc_metadata
            )

        @Authentication.check_token_for_renewal
        async def rollback(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.Rollback(to_proto_guid(self.session_id),
                metadata = self.grpc_metadata)

        @Authentication.check_token_for_renewal
        async def commit(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.Commit(to_proto_guid(self.session_id),
                metadata = self.grpc_metadata)

    def __init__(self, host, port, secure_connection: bool,
        authentication: bool = False, authentication_spn: str = None, authentication_upn: str = None):  # this will be refactored to have less params
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

        if authentication:
            self.auth = Authentication(self.mesh_service, authentication_spn, authentication_upn)
            self.grpc_metadata = (
                ('authorization', self.auth.get_token()),
            )
        else:
            self.auth: Authentication = None
            self.grpc_metadata = ()

    async def get_version(self):
        """
        |coro|
        """
        response = await self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())
        return response

    @Authentication.check_token_for_renewal
    async def get_user_identity(self):
        """
        |coro|
        """
        await self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty(),
            metadata = self.grpc_metadata)

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
