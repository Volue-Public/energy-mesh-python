import asyncio
import uuid
from datetime import datetime
from volue.mesh.aio import Connection
from volue.mesh.examples import _get_connection_info


async def read_timeseries_points_async(session: Connection.Session):
    """Showing how to read timeseries points."""

    # Define the timeseries identifiers
    timeseries_full_name = "Resource/SimpleThermalTestResourceCatalog/chimney2TimeSeriesRaw"
    timeseries_id = uuid.UUID("00000003-0003-0000-0000-000000000000")

    # Defining a time interval to read timeseries from
    start = datetime(2016, 1, 1, 6, 0, 0)
    end = datetime(2016, 1, 1, 8, 0, 0)

    # Indicate that these two functions can be run concurrently
    full_name_timeseries, id_timeseries = await asyncio.gather(
        session.read_timeseries_points(start_time=start, end_time=end, full_name=timeseries_full_name),
        session.read_timeseries_points(start_time=start, end_time=end, uuid_id=timeseries_id)
    )
    for ts in full_name_timeseries:
        print(f"Timeseries found using id contains {ts.number_of_points}.")
    for ts in id_timeseries:
        print(f"Timeseries found using full name contains {ts.number_of_points}.")


async def main(address, port, secure_connection):
    """Showing how to get timeseries points asynchronously."""
    connection = Connection(address, port, secure_connection)

    async with connection.create_session() as session:
        await read_timeseries_points_async(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    asyncio.run(main(address, port, secure_connection))
