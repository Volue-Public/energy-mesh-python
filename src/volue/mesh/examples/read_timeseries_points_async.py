import asyncio
import uuid
from datetime import datetime

from volue.mesh.aio import Connection
from volue.mesh.examples import _get_connection_info


async def read_timeseries_points_async(session: Connection.Session):
    """Showing how to read timeseries points."""

    # Define the timeseries identifiers
    timeseries_full_name = (
        "Resource/SimpleThermalTestResourceCatalog/chimney2TimeSeriesRaw"
    )
    timeseries_id = uuid.UUID("00000003-0003-0000-0000-000000000000")

    # Defining a time interval to read timeseries from.
    # If no time zone is provided then it will be treated as UTC.
    start = datetime(2016, 1, 1, 6, 0, 0)
    end = datetime(2016, 1, 1, 8, 0, 0)

    # Indicate that these two functions can be run concurrently
    full_name_timeseries, id_timeseries = await asyncio.gather(
        session.read_timeseries_points(
            target=timeseries_full_name, start_time=start, end_time=end
        ),
        session.read_timeseries_points(
            target=timeseries_id, start_time=start, end_time=end
        ),
    )
    print(
        f"Timeseries found using id contains {full_name_timeseries.number_of_points}."
    )
    print(
        f"Timeseries found using full name contains {id_timeseries.number_of_points}."
    )


async def main(address, port, root_pem_certificate):
    """Showing how to get timeseries points asynchronously."""
    connection = Connection(address, port, root_pem_certificate)

    async with connection.create_session() as session:
        await read_timeseries_points_async(session)


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    asyncio.run(main(address, port, root_pem_certificate))
