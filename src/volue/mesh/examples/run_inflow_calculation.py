import asyncio
from datetime import datetime

import helpers

import volue.mesh.aio
from volue import mesh


def sync_run_inflow_calculation(address, port, root_pem_certificate):
    print("connecting...")
    connection = mesh.Connection(address, port, root_pem_certificate)

    with connection.create_session() as session:
        start_time = datetime(2021, 1, 1)
        end_time = datetime(2021, 1, 2)

        print("running inflow calculation...")

        try:
            for response in session.run_inflow_calculation(
                "Mesh", "Area", "WaterCourse", start_time, end_time
            ):
                if isinstance(response, mesh.LogMessage):
                    print(
                        f"[{logging.getLevelName(response.level)}] {response.message}"
                    )
            print("done")
        except Exception as e:
            print(f"failed to run inflow calculation: {e}")


async def async_run_inflow_calculation(address, port, root_pem_certificate):
    print("connecting...")
    connection = mesh.aio.Connection(address, port, root_pem_certificate)

    async with connection.create_session() as session:
        start_time = datetime(2021, 1, 1)
        end_time = datetime(2021, 1, 2)

        print("running inflow calculation...")

        try:
            async for response in session.run_inflow_calculation(
                "Mesh", "Area", "WaterCourse", start_time, end_time
            ):
                if isinstance(response, mesh.LogMessage):
                    print(
                        f"[{logging.getLevelName(response.level)}] {response.message}"
                    )
            print("done")
        except Exception as e:
            print(f"failed to run inflow calculation: {e}")


if __name__ == "__main__":
    address, port, root_pem_certificate = helpers.get_connection_info()
    sync_run_inflow_calculation(address, port, root_pem_certificate)
    asyncio.run(async_run_inflow_calculation(address, port, root_pem_certificate))
