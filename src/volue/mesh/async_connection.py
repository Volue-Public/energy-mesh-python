from typing import Optional

import grpc
import uuid

from google import protobuf

from volue.mesh.timeserie import Timeserie
from volue.mesh.common import guid_to_uuid, uuid_to_guid
from volue.mesh.proto import mesh_pb2
from volue.mesh.credentials import Credentials
from volue.mesh.connection import Connection


class AsyncConnection(Connection):

    def __init__(self, host, port, secure_connection: bool):
        """
        """
        target = f'{host}:{port}'
        if not secure_connection:
            self.channel = grpc.aio.insecure_channel(
                target=target
            )
        else:
            credentials: Credentials = Credentials()
            self.channel = grpc.aio.secure_channel(
                target=target,
                credentials=credentials.channel_creds
            )

        super().__init__(host, port, secure_connection)

    async def get_version(self):
        """
        |coro|
        """
        response = await self.stub.GetVersion(protobuf.empty_pb2.Empty())
        return response

    async def start_session(self) -> uuid.UUID:
        """
        |coro|

        Raises:
            grpc.RpcError:

        """
        reply = await self.stub.StartSession(protobuf.empty_pb2.Empty())
        self.session_id = guid_to_uuid(reply.bytes_le)

        return self.session_id

    async def end_session(self) -> None:
        """
        |coro|

        Raises:
            grpc.RpcError:
        """
        await self.stub.EndSession(uuid_to_guid(self.session_id))
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

        reply = await self.stub.ReadTimeseries(
            mesh_pb2.ReadTimeseriesRequest(
                session_id=uuid_to_guid(self.session_id),
                object_id=object_id,
                interval=interval
            )
        )
        return reply

    async def write_timeseries_points(
            self,
            interval: mesh_pb2.UtcInterval,
            timeserie: Timeserie,
            timskey: int = None,
            guid: uuid.UUID = None,
            full_name: str = None) -> None:
        """
        |coro|

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

        await self.stub.WriteTimeseries(
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
        await self.stub.Rollback(uuid_to_guid(self.session_id))

    async def commit(self) -> None:
        """
        |coro|

        Raises:
            grpc.RpcError:
        """
        await self.stub.Commit(uuid_to_guid(self.session_id))
