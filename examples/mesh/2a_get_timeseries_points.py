import string
import uuid
from volue import mesh
from volue.mesh import check_result, mesh_pb2


def print_timeseries_points(timeseries, name, verbose=False):
    n = 0
    for segment in timeseries.segments:
        for point in segment.points:
            if verbose:
                print(f"{point.timestamp} : {point.value}")
            n += 1
    print(f"Received {n} points for timeseries: {name}")

def my_error_handler(mesh_reply):
    if (mesh_reply is None):
        exit()
    result = mesh.check_result(mesh_reply)
    if (result != mesh.Status.OK):
        exit()

if __name__ == "__main__":
    # Prepare a connection
    connection = mesh.Connection()
    # Print version info
    version_info = connection.get_version()
    print(version_info.full_version)

    # Start session
    connection.start_session()

    # Preapare the request
    timskey = 2125
    interval = mesh_pb2.UtcInterval(
        start_time=637450560000000000, end_time=637451424000000000
    )

    # Send request, and wait for reply
    timeseries = connection.get_timeseries_points(
        timskey=timskey,
        interval=interval
    )

    # Lets have a look at what we got
    print_timeseries_points(timeseries, str(timskey))

    # Lets try with a guid instead
    # entry_id = uuid.UUID("3F639110-D1D5-440C-A3D1-09E75D333DFF")
    entry_id = uuid.UUID("3F639110-D1D5-440C-A3D1-09E75D333DFD")
    timeseries = connection.get_timeseries_points(
        entry_id=entry_id,
        interval=interval
    )
    
    check_result(timeseries)
    
    print_timeseries_points(timeseries, str(entry_id))

    connection.end_session()
