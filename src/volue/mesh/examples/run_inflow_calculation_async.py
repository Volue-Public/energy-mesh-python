import asyncio
from datetime import datetime

from volue import mesh
import volue.mesh.aio

from volue.mesh.examples import _get_connection_info


async def main(address, port, root_pem_certificate):
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
                pass
            print("done")
        except Exception as e:
            print(f"failed to run inflow calculation: {e}")


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    asyncio.run(main(address, port, root_pem_certificate))
