from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh import Connection
from volue.examples.utility.print import get_connection_info

import asyncio


def main(address, port, secure_connection):
    print("Synchronous get version: ")
    connection = Connection(address, port, secure_connection)
    version_info = connection.get_version()
    print(version_info.full_version)

    print("Asynchronous get version: ")
    connection = AsyncConnection(address, port, secure_connection)
    version_info = asyncio.get_event_loop().run_until_complete(connection.get_version())
    print(version_info.full_version)


if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.

    address, port, secure_connection = get_connection_info()
    main(address, port, secure_connection)