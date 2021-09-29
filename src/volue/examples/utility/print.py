import pyarrow
from volue.mesh.proto import mesh_pb2
import sys


def get_connection_info():
    address = "localhost"
    port = 50051
    secure_connection = False

    if len(sys.argv) > 1:
        address = sys.argv[1]
        port = int(sys.argv[2])
        secure_connection = sys.argv[3] == "True"

    return address, port, secure_connection

def print_timeseries_points(reply: mesh_pb2.ReadTimeseriesResponse, name: str) -> None:
    """Helper function to print content of a timeseries response from the the gRPC server."""

    print(f"Reply contains {len(reply.timeseries)} timeseries")
    n = 0
    for timeserie in reply.timeseries:
        reader = pyarrow.ipc.open_stream(timeserie.data)
        pandas = reader.read_pandas()
        print(pandas)
        print(reader.schema)
        n += 1
    print(f"Received {len(pandas)} points for timeseries: {name}")
