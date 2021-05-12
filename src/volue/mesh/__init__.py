"""Client library for Volue Energy's Mesh software."""

__version__ = "0.1.0"

import os
import grpc
import string
import uuid

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from google import protobuf


def uuid_to_guid(id : uuid.UUID) -> mesh_pb2.Guid:
    if (id is None):
        return None
    return mesh_pb2.Guid(bytes_le=id.bytes_le)


def guid_to_uuid(id : mesh_pb2.Guid) -> uuid.UUID:
    if (id is None):
        return None
    return uuid.UUID(bytes_le=id.bytes_le)


class Credentials:
    def __init__(self):
        self.server_cert_path = os.path.join(
            os.path.dirname(__file__),
            'cert/server_self_signed_crt.pem')

        with open(self.server_cert_path, 'rb') as file:
            self.server_cert = file.read()

        self.channel_creds = grpc.ssl_channel_credentials(
            root_certificates=self.server_cert)


class AsyncConnection:
    def __init__(self):
        self.credentials = Credentials()
        self.channel = grpc.aio.secure_channel(
            'localhost:50051',
            self.credentials.channel_creds)
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)
        self.session_id = None

    async def get_version(self):
        return await self.stub.GetVersion(protobuf.empty_pb2.Empty())

    async def get_timeseries_points(self, 
            interval : mesh_pb2.UtcInterval, 
            timskey : int = None,
            entry_id : uuid.UUID = None,
            search_string : string = None):
        
        timeseries_id = mesh_pb2.TimeseriesId(
            timskey=timskey,
            entry_id=uuid_to_guid(entry_id),
            search_string=search_string)

        return await self.stub.GetTimeseriesPoints(
            mesh_pb2.GetTimeseriesPointsRequest(
                session_id=self.session_id,
                timeseries_id=timeseries_id,
                interval=interval
            )
        )
    
    async def end_session(self):
        if (self.session_id is not None):
            await self.stub.EndSession(self.session_id)
            self.session_id = None

    async def start_session(self):
        if (self.session_id is None):
            self.session_id = await self.stub.StartSession(protobuf.empty_pb2.Empty())
        return guid_to_uuid(self.session_id)

    async def edit_timeseries_points(self, 
            interval : mesh_pb2.UtcInterval, 
            points: mesh_pb2.TimeseriesSegment,
            timskey : int = None,
            entry_id : uuid.UUID = None,
            search_string : string = None):
        
        timeseries_id = mesh_pb2.TimeseriesId(
            timskey=timskey,
            entry_id=uuid_to_guid(entry_id),
            search_string=search_string)

        return await self.stub.EditTimeseriesPoints(
            mesh_pb2.EditTimeseriesPointsRequest(
                session_id=self.session_id,
                timeseries_id=timeseries_id,
                interval=interval,
                segment=points
            )
        )

    async def rollback(self):
        return await self.stub.Rollback(self.session_id)

    async def commit(self):
        return await self.stub.Commit(self.session_id)


class Connection:
    def __init__(self):
        self.credentials = Credentials()
        self.channel = grpc.secure_channel(
            'localhost:50051',
            self.credentials.channel_creds)
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)
        self.session_id = None

    def get_version(self):
        return self.stub.GetVersion(protobuf.empty_pb2.Empty())

    def get_timeseries_points(self, 
            interval : mesh_pb2.UtcInterval, 
            timskey : int = None,
            entry_id : uuid.UUID = None,
            search_string : string = None):
        
        timeseries_id = mesh_pb2.TimeseriesId(
            timskey=timskey,
            entry_id=uuid_to_guid(entry_id),
            search_string=search_string)

        return self.stub.GetTimeseriesPoints(
            mesh_pb2.GetTimeseriesPointsRequest(
                session_id=self.session_id,
                timeseries_id=timeseries_id,
                interval=interval
            )
        )
    
    def end_session(self):
        if (self.session_id is not None):
            self.stub.EndSession(self.session_id)
            self.session_id = None

    def start_session(self):
        if (self.session_id is None):
            self.session_id = self.stub.StartSession(protobuf.empty_pb2.Empty())
        return guid_to_uuid(self.session_id)

    def edit_timeseries_points(self, 
            interval : mesh_pb2.UtcInterval, 
            points: mesh_pb2.TimeseriesSegment,
            timskey : int = None,
            entry_id : uuid.UUID = None,
            search_string : string = None):
        
        timeseries_id = mesh_pb2.TimeseriesId(
            timskey=timskey,
            entry_id=uuid_to_guid(entry_id),
            search_string=search_string)

        return self.stub.EditTimeseriesPoints(
            mesh_pb2.EditTimeseriesPointsRequest(
                session_id=self.session_id,
                timeseries_id=timeseries_id,
                interval=interval,
                segment=points
            )
        )

    def rollback(self):
        return self.stub.Rollback(self.session_id)

    def commit(self):
        return self.stub.Commit(self.session_id)
