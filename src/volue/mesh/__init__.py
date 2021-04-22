"""Client library for Volue Energy's Mesh software."""

__version__ = "0.0.0"

import asyncio
import grpc

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from volue import mesh


async def async_get_version():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = mesh_pb2_grpc.MeshServiceStub(channel)
        return await stub.GetVersion(mesh_pb2.Null())


def get_version_string():
    server_version = asyncio.run(async_get_version())
    return (
        "\n\nServer: "
        + server_version.full_version
        + "\nClient: "
        + mesh.__version__
        + "\n"
    )


async def async_get_timeseries_points(timskey, interval):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = mesh_pb2_grpc.MeshServiceStub(channel)
        timeseries = await stub.GetTimeseriesPoints(
            mesh_pb2.GetTimeseriesPointsRequest(
                timskey=timskey, interval=interval
            )
        )
        return timeseries


def get_timeseries_points(timskey, start_time, end_time):
    interval = mesh_pb2.UtcInterval(start_time=start_time, end_time=end_time)
    return asyncio.run(async_get_timeseries_points(timskey, interval))
