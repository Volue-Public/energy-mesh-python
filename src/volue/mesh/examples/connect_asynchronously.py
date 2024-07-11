import asyncio

import helpers

from volue.mesh.aio import Connection


async def get_version(connection):
    """Showing how to get the server version."""
    print("1. Requesting server version")
    version = await connection.get_version()
    print(f"2. Server version is {version.version}")


async def start_and_end_session(session):
    """Showing how to start and end a session."""
    print("A. Starting session")
    await session.open()
    print("B. Ending session")
    await session.close()


async def main(address, tls_root_pem_cert):
    """Showing how to connect to a server and run two tasks concurrently."""
    # Creating a connection, but not sending any requests yet.

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    # Indicate that these two functions can be run concurrently.
    await asyncio.gather(
        get_version(connection), start_and_end_session(connection.create_session())
    )


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    asyncio.run(main(address, tls_root_pem_cert))
    print("Done")

# Outputs:
# 1. Requesting server version
# A. Starting session
# 2. Server version is 1.12.5.0-dev
# B. Ending session
# Done
