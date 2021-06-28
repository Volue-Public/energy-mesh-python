import uuid
from volue import mesh
from utility.print import print_timeseries_points
import utility.test_data as td

if __name__ == "__main__":
    # Prepare a connection
    connection = mesh.Connection()

    # Print version info
    version_info = connection.get_version()
    print(version_info.full_version)

    # Start session
    connection.start_session()

    # Preapare the request
    timskey = td.eagle_wind.timskey
    interval = mesh.mesh_pb2.UtcInterval(
        start_time=td.eagle_wind.start_time, end_time=td.eagle_wind.end_time
    )

    # Send request, and wait for reply
    timeseries = connection.read_timeseries_points(
        timskey=timskey,
        interval=interval
    )

    # Lets have a look at what we got
    print_timeseries_points(timeseries, str(timskey))

    # Lets try with a guid instead
    guid = uuid.UUID(td.eagle_wind.guid)
    timeseries = connection.read_timeseries_points(
        guid=guid,
        interval=interval
    )

    print_timeseries_points(timeseries, str(guid), True)

    connection.end_session()
