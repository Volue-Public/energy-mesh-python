import sys
if len(sys.argv) > 1:
    address = sys.argv[1]
    port = int(sys.argv[2])
    secure_connection = sys.argv[3] == "True"

import asyncio
from volue import mesh


async def async_print_version() -> None:

    # create a connection object that will be used
    async_connection = mesh.AsyncConnection(address, port, secure_connection)

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

if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.
    
    print("Synchronous get version: ")
    connection = mesh.Connection(address, port, secure_connection)
    version_info = connection.get_version()

    print(version_info.full_version)

    ret = connection.start_session()
    print("Started session with ID: " + str(connection.session_id))

    ret = connection.end_session()
    print("Closed session.")

    asyncio.run(async_print_version())
