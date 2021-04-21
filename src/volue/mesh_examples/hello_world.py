from __future__ import print_function
import logging

import grpc
import logging
import threading
import time
import asyncio

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc

async def AsyncServerVersion():
    async with grpc.aio.insecure_channel('localhost:50051') as channel: 
        stub = mesh_pb2_grpc.MeshServiceStub(channel)
        return await stub.GetVersion(mesh_pb2.Null())

async def SayHello(threadName) -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel: 
        stub = mesh_pb2_grpc.MeshServiceStub(channel)
        response = await stub.SayHello(mesh_pb2.HelloRequest(name='pjaall'))
        logging.info("Thread %s received %s", threadName, response.message)

async def GetTimeseriesPoints(threadName) -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = mesh_pb2_grpc.MeshServiceStub(channel)
        theInterval = mesh_pb2.UtcInterval( start_time = 637450560000000000, end_time = 637451424000000000 )
        theTimskey = 2125;
        tsPointsResponse = await stub.GetTimeseriesPoints(mesh_pb2.GetTimeseriesPointsRequest(timskey=theTimskey, interval = theInterval))
        n = 0
        for segment in tsPointsResponse.segments:
            for point in segment.points:
                n+=1
        logging.info("Thread %s received %s points.", threadName, str(n))

def thread_function(name) -> None:
    logging.info("Thread %s: starting", name)
    for x in range(10):
        asyncio.run(SayHello(threadName=name));
        asyncio.run(GetTimeseriesPoints(threadName=name));
    logging.info("Thread %s: finishing", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")

    version = asyncio.run(AsyncServerVersion())
    logging.info("Mesh server: %s", version.full_version)
    
    threadList = []
    for x in range(10):
        threadList.append(threading.Thread(target=thread_function, args=(x,)))
    
    logging.info("Main    : before running thread")
    for t in threadList:
        t.start()
    logging.info("Main    : wait for the thread to finish")
    for t in threadList:
        t.join()
    logging.info("Main    : all done")