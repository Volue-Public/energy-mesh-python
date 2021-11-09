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
            session_id: uuid = None):
            """

            Args:
                mesh_service:
                session_id:
            """
            self.session_id: uuid = session_id
            self.mesh_service: mesh_pb2_grpc.MeshServiceStub = mesh_service

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
            self.session_id = from_proto_guid(reply)
            return reply

        async def close(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.EndSession(to_proto_guid(self.session_id))
            self.session_id = None

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
                ))
            return read_proto_reply(reply)

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
                ))

        async def rollback(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.Rollback(to_proto_guid(self.session_id))

        async def commit(self) -> None:
            """
            |coro|

            Raises:
                grpc.RpcError:
            """
            await self.mesh_service.Commit(to_proto_guid(self.session_id))

    def __init__(self, host, port, secure_connection: bool,
                 authentication_parameters: Authentication.Parameters = None):
        """
        """
        target = f'{host}:{port}'
        self.auth_metadata_plugin = None

        # There are 3 possible async connection types:
        # - insecure (without TLS)
        # - with TLS
        # - with TLS and Kerberos authentication
        #   (authentication requires TLS for encrypting auth tokens)
        if not secure_connection:
            # insecure connection (without TLS)
            channel = grpc.aio.insecure_channel(
                target=target
            )
        else:
            credentials: Credentials = Credentials()

            # authentication requires TLS
            if authentication_parameters:
                self.auth_metadata_plugin = Authentication(
                    authentication_parameters, target, credentials.channel_creds)
                call_credentials = grpc.metadata_call_credentials(self.auth_metadata_plugin)

                composite_credentials = grpc.composite_channel_credentials(
                    credentials.channel_creds,
                    call_credentials,
                )

                # connection using TLS and Kerberos authentication
                channel = grpc.aio.secure_channel(
                    target=target,
                    credentials=composite_credentials
                )
            else:
                # connection using TLS (no Kerberos authentication)
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

    async def get_user_identity(self):
        """
        |coro|
        """
        response = await self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty())
        return response

    async def revoke_access_token(self):
        """
        Revokes Mesh token if no longer needed.
        """
        self.auth_metadata_plugin.revoke_access_token()
        token = protobuf.wrappers_pb2.StringValue(value = self.auth_metadata_plugin.token)
        await self.mesh_service.RevokeAccessToken(token)

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
