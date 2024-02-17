import asyncio
import uuid
from datetime import datetime

from volue.mesh.aio import Connection
import helpers


async def read_timeseries_points_async(session: Connection.Session):
    """Showing how to read time series points."""

    # Define the time series identifier, it can be:
    # - time series key of a physical time series
    # - path of a time series attribute that is connected to a physical time series
    # - ID of a time series attribute that is connected to a physical time series
    timeseries_key = 3
    timeseries_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.TsRawAtt"
    timeseries_attribute_id = uuid.UUID("e5df77a9-8b60-4b0a-aa1b-3c3957c538a0")

    # Defining a time interval to read time series from.
    # If no time zone is provided then it will be treated as UTC.
    start = datetime(2016, 1, 1, 6, 0, 0)
    end = datetime(2016, 1, 1, 8, 0, 0)

    # Send request to read time series based on time series key.
    timeseries = await session.read_timeseries_points(
        target=timeseries_key, start_time=start, end_time=end
    )
    print(f"Read {timeseries.number_of_points} points using time series key.")
    print(timeseries.arrow_table.to_pandas())

    # Send requests to read time series based on time series attribute path.
    timeseries = await session.read_timeseries_points(
        target=timeseries_attribute_path, start_time=start, end_time=end
    )
    print(
        f"Read {timeseries.number_of_points} points using time series attribute path."
    )
    print(timeseries.arrow_table.to_pandas())

    # Send requests to read time series based on time series attribute ID.
    # Attribute IDs are auto-generated when an object is created.
    # That is why we can't use any fixed ID in this example and the code is commented out.
    # timeseries = await session.read_timeseries_points(
    #     target=timeseries_attribute_id, start_time=start, end_time=end
    # )
    # print(f"Read {timeseries.number_of_points} points using time series attribute ID.")
    # print(timeseries.arrow_table.to_pandas())


async def main(address, port, root_pem_certificate):
    """Showing how to get time series points asynchronously."""
    connection = Connection(address, port, root_pem_certificate)

    async with connection.create_session() as session:
        await read_timeseries_points_async(session)


if __name__ == "__main__":
    address, port, root_pem_certificate = helpers.get_connection_info()
    asyncio.run(main(address, port, root_pem_certificate))
