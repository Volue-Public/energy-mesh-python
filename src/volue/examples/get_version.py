from volue.mesh.async_connection import AsyncConnection
from volue.mesh.connection import Connection
from volue.examples.utility.print import get_connection_info

import asyncio


async def async_print_version(address, port, secure_connection) -> None:

    # create a connection object that will be used
    async_connection = AsyncConnection(address, port, secure_connection)

    # request version
    future = async_connection.get_version()

    # do some other work, until...
    # ... we actually need the version
    version_info = await future
    print(version_info.full_version)

    ret = await async_connection.start_session()
    print(
        "Asynchronously started session with ID: "
        f"{async_connection.session_id}")

    ret = await async_connection.end_session()
    print("Asynchronously closed session.")


def main(address, port, secure_connection):
    print("Synchronous get version: ")
    connection = Connection(address, port, secure_connection)
    version_info = connection.get_version()
    print(version_info.full_version)
    ret = connection.start_session()
    print("Started session with ID: " + str(connection.session_id))
    ret = connection.end_session()
    print("Closed session.")
    asyncio.run(async_print_version(address, port, secure_connection))


if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.

    address, port, secure_connection = get_connection_info()

    main(address, port, secure_connection)