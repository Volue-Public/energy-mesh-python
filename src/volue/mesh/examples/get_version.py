import asyncio

import helpers

from volue.mesh import Connection
from volue.mesh.aio import Connection as AsyncConnection


def sync_get_version(address, port, root_pem_certificate):
    print("Synchronous get version:")
    connection = Connection(address, port, root_pem_certificate)
    version_info = connection.get_version()
    print(version_info.version)


async def async_get_version(
    address,
    port,
    root_pem_certificate,
):
    print("Asynchronous get version:")
    connection = AsyncConnection(address, port, root_pem_certificate)
    version_info = await connection.get_version()
    print(version_info.version)


def main(address, port, root_pem_certificate):
    """Showing how to send get the server version both sequentially and concurrently."""

    sync_get_version(
        address,
        port,
        root_pem_certificate,
    )
    asyncio.run(async_get_version(address, port, root_pem_certificate))


if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.

    address, port, root_pem_certificate = helpers.get_connection_info()
    main(address, port, root_pem_certificate)
