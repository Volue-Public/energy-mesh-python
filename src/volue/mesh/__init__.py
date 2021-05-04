"""Client library for Volue Energy's Mesh software."""

__version__ = "0.1.0"

import os
import grpc

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from google import protobuf


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
            "localhost:50051",
            self.credentials.channel_creds)
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)

    async def get_version(self):
        return await self.stub.GetVersion((protobuf.empty_pb2.Empty()))

    async def get_timeseries_points(self, timskey, interval):
        return await self.stub.GetTimeseriesPoints(
            mesh_pb2.GetTimeseriesPointsRequest(
                timskey=timskey, interval=interval
            )
        )


class Connection:
    def __init__(self):
        self.credentials = Credentials()
        self.channel = grpc.secure_channel(
            'localhost:50051',
            self.credentials.channel_creds)
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)

    def get_version(self):
        return self.stub.GetVersion((protobuf.empty_pb2.Empty()))

    def get_timeseries_points(self, timskey, interval):
        return self.stub.GetTimeseriesPoints(
            mesh_pb2.GetTimeseriesPointsRequest(
                timskey=timskey, interval=interval
            )
        )
