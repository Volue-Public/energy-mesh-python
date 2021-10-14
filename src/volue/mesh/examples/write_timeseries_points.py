import pyarrow as pa
from volue.mesh import Connection, Timeseries, dot_net_ticks_to_protobuf_timestamp, eagle_wind
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.mesh.examples import _get_connection_info


def write_timeseries_points(session: Connection.Session):
    """Showing how to write timeseries points."""

    # Defining a time interval to write timeseries to
    interval = UtcInterval(
        start_time=dot_net_ticks_to_protobuf_timestamp(eagle_wind.start_time_ticks),
        end_time=dot_net_ticks_to_protobuf_timestamp(eagle_wind.end_time_ticks)
    )

    # Defining the data we want to write
    arrays = [
        pa.array([1462060800, 1462064400, 1462068000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    timeseries = Timeseries(table=table)

    # Send request to write timeseries based on timskey
    session.write_timeseries_points(
        timskey=eagle_wind.timskey,
        interval=interval,
        timeserie=timeseries
    )

    # TODO read? commit?


def main(address, port, secure_connection):
    """Showing how to write timeseries points."""
    connection = Connection(address, port, secure_connection)

    with connection.create_session() as session:
        write_timeseries_points(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)

