import asyncio
from volue import mesh


def my_error_handler(mesh_reply):
    if (mesh_reply is None):
        exit()
    result = mesh.check_result(mesh_reply)
    if (result != mesh.Status.OK):
        exit()


async def async_print_version() -> None:
    async_connection = mesh.AsyncConnection()
    # request version
    future = async_connection.get_version()
    # do some other work, until...
    # ... we actually need the version
    version_info = await future
    print(version_info.full_version)
    my_error_handler(version_info)

    ret = await async_connection.start_session()
    my_error_handler(ret)
    print(
        "Asynchronously started session with ID: "
        f"{async_connection.session_id}")

    ret = await async_connection.end_session()
    my_error_handler(ret)
    print("Asynchronously closed session.")

if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.

    print("Synchronous get version: ")
    connection = mesh.Connection()
    version_info = connection.get_version()
    my_error_handler(version_info)

    print(version_info.full_version)

    ret = connection.start_session()
    my_error_handler(ret)

    print("Started session with ID: " + str(connection.session_id))

    ret = connection.end_session()
    my_error_handler(ret)
    print("Closed session.")

    asyncio.run(async_print_version())
