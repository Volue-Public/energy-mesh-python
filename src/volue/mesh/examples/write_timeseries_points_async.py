import asyncio
import pyarrow as pa
from datetime import datetime
from volue.mesh.aio import Connection
from volue.mesh import Timeseries
from volue.mesh.tests.test_utilities.utilities import eagle_wind
from volue.mesh.examples import _get_connection_info


async def write_timeseries_points(session: Connection.Session):
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
    timeseries = Timeseries(table=table, start_time=start, end_time=end, timskey=eagle_wind.timskey)

    # Send request to write timeseries based on timskey
    await session.write_timeseries_points(
        timeserie=timeseries
    )

    # Commit the changes to the database
    # await session.commit()


async def main(address, port, secure_connection):
    """Showing how to write timeseries points."""
    connection = Connection(address, port, secure_connection)

    async with connection.create_session() as session:
        await write_timeseries_points(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    asyncio.run(main(address, port, secure_connection))
