import uuid
from volue.mesh import Connection, dot_net_ticks_to_protobuf_timestamp, eagle_wind
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.mesh.examples import _get_connection_info


def read_timeseries_points(session: Connection.Session):
    """Showing how to read timeseries points."""

    # Defining a time interval to read timeseries from
    interval = UtcInterval(
        start_time=dot_net_ticks_to_protobuf_timestamp(eagle_wind.start_time_ticks),
        end_time=dot_net_ticks_to_protobuf_timestamp(eagle_wind.end_time_ticks)
    )

    # Send request to read timeseries based on timskey
    timskey = eagle_wind.timskey
    timeseries = session.read_timeseries_points(
        timskey=timskey,
        interval=interval
    )
    print(f"Read {timeseries.number_of_points} points")

    # Send request to read timeseries based on guid
    guid = uuid.UUID(eagle_wind.guid)
    timeseries = session.read_timeseries_points(
        guid=guid,
        interval=interval
    )
    print(f"Read {timeseries.number_of_points} points")


def main(address, port, secure_connection):
    """Showing how to get timeseries points."""
    connection = Connection(address, port, secure_connection)

    with connection.create_session() as session:
        read_timeseries_points(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)
