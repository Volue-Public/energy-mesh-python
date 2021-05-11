import asyncio
from volue import mesh


async def async_print_version() -> None:
    async_connection = mesh.AsyncConnection()
    # request version
    future = async_connection.get_version()
    # do some other work, until...
    # ... we actually need the version
    version_info = await future
    print(version_info.full_version)

    session_id = await async_connection.start_session()
    print(session_id)

    await async_connection.end_session()


if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.

    print("Synchronous get version: ")
    connection = mesh.Connection()
    version_info = connection.get_version()
    print(version_info.full_version)

    session_id = connection.start_session()
    print(str(session_id))

    connection.end_session()

    print("Asynchronous get version: ")
    asyncio.run(async_print_version())
