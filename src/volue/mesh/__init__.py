"""Client library for Volue Energy's Mesh software."""

__version__ = "0.1.0"

import grpc

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from google import protobuf


class AsyncConnection:
    def __init__(self):
        self.channel = grpc.aio.insecure_channel("localhost:50051")
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
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = mesh_pb2_grpc.MeshServiceStub(self.channel)

    def get_version(self):
        return self.stub.GetVersion((protobuf.empty_pb2.Empty()))

    def get_timeseries_points(self, timskey, interval):
        return self.stub.GetTimeseriesPoints(
            mesh_pb2.GetTimeseriesPointsRequest(
                timskey=timskey, interval=interval
            )
        )
