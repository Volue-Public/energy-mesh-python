"""Client library for Volue Energy's Mesh software."""

__version__ = "0.1.0"

import os
import grpc
import string
import uuid

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from volue.mesh.proto.mesh_pb2 import Status
from google import protobuf

# Purpose
# Usability: 
# . Intuitive
# . Interactions: 
#   . Feedback 
#   . Input
#   . Flow
# . Predictable: 
#   General flow of an API call (Consistent):
#     1. Call the desired function on a connection
#     2. Check status. All replys from Mesh has a status field.
#     3. Use returned data
#   . Adaptable 
#   . Discoverable
# Constraints

def uuid_to_guid(id : uuid.UUID) -> mesh_pb2.Guid:
    if (id is None):
        return None
    return mesh_pb2.Guid(bytes_le=id.bytes_le)


def guid_to_uuid(id : mesh_pb2.Guid) -> uuid.UUID:
    if (id is None):
        return None
    return uuid.UUID(bytes_le=id.bytes_le)

def check_result(reply):
    if (reply.status.status_code is not Status.StatusCode.OK):
        # TODO: Handle specific error codes here?
        print (F"Error response from Mesh server:\n" \
            F"  StatusCode: { reply.status.status_code }\n" \
            F"  ErrorText: \"{ reply.status.error_text }\"")
    
    return reply.status.status_code


class Credentials:
    def __init__(self):
        self.server_cert_path = os.path.join(
            os.path.dirname(__file__),
            'cert/server_self_signed_crt.pem')

        with open(self.server_cert_path, 'rb') as file:
            self.server_cert = file.read()

        self.channel_creds = grpc.ssl_channel_credentials(
            root_certificates=self.server_cert)


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
                session_id=uuid_to_guid(self.session_id),
                timeseries_id=timeseries_id,
                interval=interval
            )
        )
    
    def end_session(self):
        if (self.session_id is not None):
            reply = self.stub.EndSession(uuid_to_guid(self.session_id))
            if (reply.status.status_code is Status.StatusCode.OK):
                self.session_id = None
            return reply
        status = mesh_pb2.Status(status_code=Status.StatusCode.OK)
        reply = mesh_pb2.StatusReply(status=status)
        return reply

    def start_session(self):
        if (self.session_id is None):
            reply = self.stub.StartSession(protobuf.empty_pb2.Empty())
            if (reply.status.status_code is Status.StatusCode.OK):
                self.session_id = guid_to_uuid(reply.session_id)
            return reply
        status = mesh_pb2.Status(status_code=Status.StatusCode.OK)
        reply = mesh_pb2.StatusReply(status=status)
        return reply

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
                session_id=uuid_to_guid(self.session_id),
                timeseries_id=timeseries_id,
                interval=interval,
                segment=points
            )
        )

    def rollback(self):
        return self.stub.Rollback(uuid_to_guid(self.session_id))

    def commit(self):
        return self.stub.Commit(uuid_to_guid(self.session_id))


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
                session_id=uuid_to_guid(self.session_id),
                timeseries_id=timeseries_id,
                interval=interval
            )
        )
    
    async def end_session(self):
        if (self.session_id is not None):
            reply = await self.stub.EndSession(uuid_to_guid(self.session_id))
            if (reply.status.status_code is Status.StatusCode.OK):
                self.session_id = None
            return reply
        status = mesh_pb2.Status(
            status_code=Status.StatusCode.INVALID_INPUT,
            error_text="No session associated with Connection object."
            )
        reply = mesh_pb2.StatusReply(status=status)
        return reply

    async def start_session(self):
        if (self.session_id is None):
            reply = await self.stub.StartSession(protobuf.empty_pb2.Empty())
            if (reply.status.status_code is Status.StatusCode.OK):
                self.session_id = guid_to_uuid(reply.session_id)
            return reply
        status = mesh_pb2.Status(
            status_code=Status.StatusCode.INVALID_INPUT,
            error_text="No session associated with Connection object."
            )
        reply = mesh_pb2.StatusReply(status=status)
        return reply

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
                session_id=uuid_to_guid(self.session_id),
                timeseries_id=timeseries_id,
                interval=interval,
                segment=points
            )
        )

    async def rollback(self):
        return await self.stub.Rollback(uuid_to_guid(self.session_id))

    async def commit(self):
        return await self.stub.Commit(uuid_to_guid(self.session_id))
