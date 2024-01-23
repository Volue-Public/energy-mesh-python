import asyncio
from datetime import datetime

from volue import mesh
import volue.mesh.aio

from volue.mesh.examples import _get_connection_info


def sync_run_simulation(address, port, root_pem_certificate):
    print("connecting...")
    connection = mesh.Connection(address, port, root_pem_certificate)

    with connection.create_session() as session:
        start_time = datetime(2023, 11, 1)
        end_time = datetime(2023, 11, 2)

        print("running simulation...")

        try:
            for response in session.run_simulation(
                "Mesh", "Cases/Demo", start_time, end_time, None, 0, False
            ):
                pass
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
                "Mesh", "Cases/Demo", start_time, end_time, None, 0, False
            ):
                pass
            print("done")
        except Exception as e:
            print(f"failed to run simulation: {e}")


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    sync_run_simulation(address, port, root_pem_certificate)
    asyncio.run(async_run_simulation(address, port, root_pem_certificate))
