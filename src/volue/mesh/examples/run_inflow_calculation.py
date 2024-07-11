import asyncio
import logging
from datetime import datetime, timedelta

import helpers

import volue.mesh.aio
from volue import mesh


def sync_run_inflow_calculation(address, tls_root_pem_cert):
    print("connecting...")

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.Connection.insecure(address)

    with connection.create_session() as session:
        start_time = datetime(2021, 1, 1)
        end_time = datetime(2021, 1, 2)

        print("running inflow calculation...")

        try:
            for response in session.run_inflow_calculation(
                "Mesh",
                "Area",
                "WaterCourse",
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
            print(f"failed to run inflow calculation: {e}")


async def async_run_inflow_calculation(address, tls_root_pem_cert):
    print("connecting...")

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.aio.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.aio.Connection.insecure(address)

    async with connection.create_session() as session:
        start_time = datetime(2021, 1, 1)
        end_time = datetime(2021, 1, 2)

        print("running inflow calculation...")

        try:
            async for response in session.run_inflow_calculation(
                "Mesh",
                "Area",
                "WaterCourse",
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
            print(f"failed to run inflow calculation: {e}")


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    sync_run_inflow_calculation(address, tls_root_pem_cert)
    asyncio.run(async_run_inflow_calculation(address, tls_root_pem_cert))
