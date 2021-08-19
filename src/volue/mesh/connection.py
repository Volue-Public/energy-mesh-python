import os
import grpc
import string
import uuid

from google import protobuf

from volue.mesh.timeserie import *
from volue.mesh.common import *
from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from volue.mesh.credentials import Credentials

class Connection:

    def __init__(self, host = 'localhost', port = '50051'):
        self.credentials = Credentials()
        address = host+':'+port
        self.channel = grpc.secure_channel(
            target = address,
            credentials = self.credentials.channel_creds
        )
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)
        self.session_id = None

    def get_version(self):
        try:
            response = self.stub.GetVersion(protobuf.empty_pb2.Empty())
        except grpc.RpcError as e:
            self.react_to_error(e)
        else:
            return response


    def start_session(self):
        if (self.session_id is None):
            try:
                reply = self.stub.StartSession(protobuf.empty_pb2.Empty())
            except grpc.RpcError as e:
                self.react_to_error(e)
            else:
                self.session_id = guid_to_uuid(reply.bytes_le)
                return reply
        return None


    def end_session(self):
        if (self.session_id is not None):
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
            full_name: string = None):

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
            full_name: string = None):

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
        return self.stub.Rollback(uuid_to_guid(self.session_id))

    def commit(self):
        return self.stub.Commit(uuid_to_guid(self.session_id))

    def react_to_error(self, e):
        # TODO need more intelligent error handling
        print(f"""
            gRPC error:
                Details:        {e.details()}
                Status code:    {e.code()}
        """)

