import pyarrow as pa
from datetime import datetime
from volue.mesh import Connection, Timeseries, eagle_wind
from volue.mesh.examples import _get_connection_info


def write_timeseries_points(session: Connection.Session):
    """Showing how to write timeseries points."""

    # Defining a time interval to write timeseries to
    start = datetime(2016, 5, 1)
    end = datetime(2016, 5, 14)

    # Defining the data we want to write
    arrays = [
        pa.array([1462060800, 1462064400, 1462068000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    timeseries = Timeseries(tables=[table], start_time=start, end_time=end, timskey=eagle_wind.timskey)

    # Send request to write timeseries based on timskey
    session.write_timeseries_points(
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

