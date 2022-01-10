import pyarrow as pa
from datetime import datetime
from volue.mesh import Connection, Timeseries
from volue.mesh.tests.test_utilities.utilities import test_timeseries_entry
from volue.mesh.examples import _get_connection_info


def write_timeseries_points(session: Connection.Session):
    """Showing how to write timeseries points."""

    # Defining a time interval to write timeseries to
    start = datetime(2016, 5, 1)
    end = datetime(2016, 5, 2)  # end time must be greater than last point to be read/written

    # Defining the data we want to write
    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]
    arrays = [
        pa.array([datetime(2016, 5, 1), datetime(2016, 5, 1, 1),  datetime(2016, 5, 1, 2)]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    timeseries = Timeseries(table=table, start_time=start, end_time=end, timskey=test_timeseries_entry.timskey)

    # Send request to write timeseries based on timskey
    session.write_timeseries_points(
        timeserie=timeseries
    )

    # Commit the changes to the database
    # session.commit()


def main(address, port, secure_connection):
    """Showing how to write timeseries points."""
    connection = Connection(address, port, secure_connection)

    with connection.create_session() as session:
        write_timeseries_points(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)

