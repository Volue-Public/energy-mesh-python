import asyncio
import grpc

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from volue import mesh

async def AsyncGetVersion():
    async with grpc.aio.insecure_channel('localhost:50051') as channel: 
        stub = mesh_pb2_grpc.MeshServiceStub(channel)
        return await stub.GetVersion(mesh_pb2.Null())

def GetVersionString():
    server_version = asyncio.run(AsyncGetVersion());
    return "\n\nServer: " + server_version.full_version + "\nClient: " + mesh.__version__ + "\n"

async def AsyncGetTimeseriesPoints(theTimskey, theInterval):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = mesh_pb2_grpc.MeshServiceStub(channel)
        tsPointsResponse = await stub.GetTimeseriesPoints(mesh_pb2.GetTimeseriesPointsRequest(timskey=theTimskey, interval = theInterval))
        return tsPointsResponse

def GetTimeseriesPoints(theTimskey, theStartTime, theEndTime):
    theInterval = mesh_pb2.UtcInterval( start_time = theStartTime, end_time = theEndTime )
    return asyncio.run(AsyncGetTimeseriesPoints(theTimskey, theInterval))
        