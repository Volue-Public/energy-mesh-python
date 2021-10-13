from volue.mesh import Connection, Timeseries, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.mesh.examples.utility.print import get_connection_info
import volue.mesh.examples.utility.test_data as td


def main(address, port, secure_connection):

    # Prepare a connection
    connection = Connection(address, port, secure_connection)

    # Start a session
    with connection.create_session() as session:

        timskey = td.eagle_wind.timskey
        interval = UtcInterval(
            start_time=dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks),
            end_time=dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks)
        )

        # Send request, and wait for reply
        timeseries = session.read_timeseries_points(
            timskey=timskey,
            interval=interval
        )

        # Lets edit some points:
        session.write_timeseries_points(
            timskey=timskey,
            interval=interval,
            timeserie=timeseries
        )
        # Let's have a look at the points again
        timeseries = session.read_timeseries_points(
            timskey=timskey,
            interval=interval)

        # Rollback
        session.rollback()
        timeseries = session.read_timeseries_points(
            timskey=timskey,
            interval=interval)

        # Edit again, and commit. Now the changes will be stored in database:
        session.write_timeseries_points(
            timskey=timskey,
            interval=interval,
            timeserie=timeseries
        )
        session.commit()


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()

    main(address, port, secure_connection)
