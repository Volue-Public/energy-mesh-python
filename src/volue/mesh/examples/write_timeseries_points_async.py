import asyncio
import pyarrow as pa
from datetime import datetime, timezone
from volue.mesh.aio import Connection
from volue.mesh import Timeseries
from volue.mesh.examples import _get_connection_info


async def write_timeseries_points(session: Connection.Session):
    """Showing how to write timeseries points."""

    # Define the timeseries identifiers
    timeseries_full_name = "Resource/SimpleThermalTestResourceCatalog/chimney2TimeSeriesRaw"

    # Defining a time interval to write timeseries to
    start = datetime(2016, 1, 1, 1, 0, 0)
    end = datetime(2016, 1, 1, 3, 0, 0) # end time must be greater than last point to be read/written

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
    timeseries = Timeseries(table=table, start_time=start, end_time=end, full_name=timeseries_full_name)

    # Send request to write timeseries based on timskey
    await session.write_timeseries_points(timeserie=timeseries)

    # Commit the changes to the database
    # await session.commit()

    # Or discard changes
    await session.rollback()


async def main(address, port, secure_connection):
    """Showing how to write timeseries points."""
    connection = Connection(address, port, secure_connection)

    async with connection.create_session() as session:
        await write_timeseries_points(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    asyncio.run(main(address, port, secure_connection))
