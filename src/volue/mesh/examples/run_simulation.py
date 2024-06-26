import asyncio
import logging
from datetime import datetime, timedelta

import helpers

import volue.mesh.aio
from volue import mesh


def sync_run_simulation(address, port, root_pem_certificate):
    print("connecting...")
    connection = mesh.Connection(address, port, root_pem_certificate)

    with connection.create_session() as session:
        start_time = datetime(2023, 11, 1)
        end_time = datetime(2023, 11, 2)

        print("running simulation...")

        try:
            for response in session.run_simulation(
                "Mesh",
                "Cases/Demo",
                start_time,
                end_time,
                return_datasets=True,
                resolution=timedelta(minutes=5),
            ):
                if isinstance(response, mesh.LogMessage):
                    print(
                        f"[{logging.getLevelName(response.level)}] {response.message}"
                    )
                elif isinstance(response, mesh.HydSimDataset):
                    print(
                        f"Received dataset {response.name} with {len(response.data)} bytes"
                    )
            print("done")
        except Exception as e:
            print(f"failed to run simulation: {e}")


async def async_run_simulation(address, port, root_pem_certificate):
    print("connecting...")
    connection = mesh.aio.Connection(address, port, root_pem_certificate)

    async with connection.create_session() as session:
        start_time = datetime(2023, 11, 1)
        end_time = datetime(2023, 11, 2)

        print("running simulation...")

        try:
            async for response in session.run_simulation(
                "Mesh",
                "Cases/Demo",
                start_time,
                end_time,
                return_datasets=True,
                resolution=timedelta(minutes=5),
            ):
                if isinstance(response, mesh.LogMessage):
                    print(
                        f"[{logging.getLevelName(response.level)}] {response.message}"
                    )
                elif isinstance(response, mesh.HydSimDataset):
                    print(
                        f"Received dataset {response.name} with {len(response.data)} bytes"
                    )
            print("done")
        except Exception as e:
            print(f"failed to run simulation: {e}")


if __name__ == "__main__":
    address, port, root_pem_certificate = helpers.get_connection_info()
    sync_run_simulation(address, port, root_pem_certificate)
    asyncio.run(async_run_simulation(address, port, root_pem_certificate))
