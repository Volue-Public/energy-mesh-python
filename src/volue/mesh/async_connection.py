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

        try:
            response = await self.stub.GetVersion(protobuf.empty_pb2.Empty())
        except grpc.RpcError as e:
            self.react_to_error(e)
        else:
            return response

    async def start_session(self):
        """
        |coro|
        """
        if (self.session_id is None):
            try:
                reply = await self.stub.StartSession(protobuf.empty_pb2.Empty())
            except grpc.RpcError as e:
                self.react_to_error(e)
            else:
                self.session_id = guid_to_uuid(reply.bytes_le)
                return reply
        return None

    async def end_session(self):
        """
        |coro|
        """
        if (self.session_id is not None):
            try:
                reply = await self.stub.EndSession(uuid_to_guid(self.session_id))
            except grpc.RpcError as e:
                self.react_to_error(e)
            else:
                self.session_id = None
                return reply
        return None

    async def read_timeseries_points(
            self,
            interval: mesh_pb2.UtcInterval,
            timskey: int = None,
            guid: uuid.UUID = None,
            full_name: str = None):
        """
        |coro|
        """

        object_id = mesh_pb2.ObjectId(
            timskey=timskey,
            guid=uuid_to_guid(guid),
            full_name=full_name)

        try:
            reply = await self.stub.ReadTimeseries(
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

    async def write_timeseries_points(
            self,
            interval: mesh_pb2.UtcInterval,
            timeserie: Timeserie,
            timskey: int = None,
            guid: uuid.UUID = None,
            full_name: str = None):
        """
        |coro|
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
            reply = await self.stub.WriteTimeseries(
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

    async def rollback(self):
        """
        |coro|
        """

        return await self.stub.Rollback(uuid_to_guid(self.session_id))

    async def commit(self):
        """
        |coro|
        """
        return await self.stub.Commit(uuid_to_guid(self.session_id))
