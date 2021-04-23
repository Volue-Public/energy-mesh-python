"""Client library for Volue Energy's Mesh software."""

__version__ = "0.0.0"

import asyncio
import grpc

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from google import protobuf
from volue import mesh


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
        self.async_connection = AsyncConnection()
        self.loop = asyncio.get_event_loop()

    def get_version(self):
        return self.loop.run_until_complete(
            self.async_connection.get_version()
            )

    def get_timeseries_points(self, timskey, interval):
        return self.loop.run_until_complete(
            self.async_connection.get_timeseries_points(
                timskey, interval
            )
        )


def get_version_string():
    conn = Connection()
    server_version = conn.get_version()
    return (
        "\n\nServer: "
        + server_version.full_version
        + "\nClient: "
        + mesh.__version__
        + "\n"
    )
