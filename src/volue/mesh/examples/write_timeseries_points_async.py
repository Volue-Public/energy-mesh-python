import asyncio
import pyarrow as pa
from datetime import datetime, timezone
from volue.mesh.aio import Connection
from volue.mesh import Timeseries
from volue.mesh.examples import _get_connection_info


async def write_timeseries_points(session: Connection.Session):
    """Showing how to write timeseries points."""

    # Define the timeseries identifiers
    timeseries_full_name = (
        "Resource/SimpleThermalTestResourceCatalog/chimney2TimeSeriesRaw"
    )

    # Defining the data we want to write
    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]
    arrays = [
        # if no time zone is provided then the timestamp is treated as UTC
        pa.array(
            [datetime(2016, 1, 1, 1), datetime(2016, 1, 1, 2), datetime(2016, 1, 1, 3)]
        ),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0]),
    ]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    timeseries = Timeseries(table=table, full_name=timeseries_full_name)

    # Send request to write timeseries based on timskey
    await session.write_timeseries_points(timeseries=timeseries)

    # Commit the changes to the database
    # await session.commit()

    # Or discard changes
    await session.rollback()


async def main(address, port, root_pem_certificate):
    """Showing how to write timeseries points."""
    connection = Connection(address, port, root_pem_certificate)

    async with connection.create_session() as session:
        await write_timeseries_points(session)


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    asyncio.run(main(address, port, root_pem_certificate))
