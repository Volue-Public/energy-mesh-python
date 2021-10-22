import asyncio
import uuid
from datetime import datetime
from volue.mesh.aio import Connection
from volue.mesh import eagle_wind
from volue.mesh.examples import _get_connection_info


async def read_timeseries_points_async(session: Connection.Session):
    """Showing how to read timeseries points."""

    # Defining a time interval to read timeseries from
    start = datetime(2016, 5, 1)
    end = datetime(2016, 5, 14)

    # Indicate that these two functions can be run concurrently
    timskey = eagle_wind.timskey
    guid = uuid.UUID(eagle_wind.guid)
    timskey_timeseries, guid_timeseries = await asyncio.gather(
        session.read_timeseries_points(start_time=start, end_time=end, timskey=timskey),
        session.read_timeseries_points(start_time=start, end_time=end, guid=guid)
    )
    for ts in timskey_timeseries:
        print(f"Timskey timeseries contains {ts.number_of_points}.")
    for ts in guid_timeseries:
        print(f"Guid timeseries contains {ts.number_of_points}.")


async def main(address, port, secure_connection):
    """Showing how to get timeseries points asynchronously."""
    connection = Connection(address, port, secure_connection)

    async with connection.create_session() as session:
        await read_timeseries_points_async(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    asyncio.run(main(address, port, secure_connection))
