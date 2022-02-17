from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh import Connection
from volue.mesh.examples import _get_connection_info

import asyncio

def main(address, port, root_certificate_path):
    """Showing how to send get the server version both sequentially and concurrently."""

    print("Synchronous get version: ")
    connection = Connection(address, port, root_certificate_path)
    version_info = connection.get_version()
    print(version_info.full_version)

    print("Asynchronous get version: ")
    connection = AsyncConnection(address, port, root_certificate_path)
    version_info = asyncio.get_event_loop().run_until_complete(connection.get_version())
    print(version_info.full_version)


if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.

    address, port, root_certificate_path = _get_connection_info()
    main(address, port, root_certificate_path)

