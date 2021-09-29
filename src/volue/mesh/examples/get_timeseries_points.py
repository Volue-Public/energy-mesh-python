from volue.mesh import Connection, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.mesh.examples.utility.print import print_timeseries_points, get_connection_info
import volue.mesh.examples.utility.test_data as td

import uuid


def main(address, port, secure_connection):

    # Prepare a connection
    connection = Connection(address, port, secure_connection)
    # Print version info
    version_info = connection.get_version()
    print(version_info.full_version)
    # Start session
    session = connection.create_session()
    session.open()
    # Preapare the request
    timskey = td.eagle_wind.timskey
    start = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks)
    end = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks)
    interval = UtcInterval(
        start_time=start,
        end_time=end
    )
    # Send request, and wait for reply
    timeseries = session.read_timeseries_points(
        timskey=timskey,
        interval=interval
    )
    # Lets have a look at what we got
    print_timeseries_points(timeseries, str(timskey))
    # Lets try with a guid instead
    guid = uuid.UUID(td.eagle_wind.guid)
    timeseries = session.read_timeseries_points(
        guid=guid,
        interval=interval
    )
    print_timeseries_points(timeseries, str(guid))
    session.close()


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    main(address, port, secure_connection)
