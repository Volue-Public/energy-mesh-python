from __future__ import print_function
import logging
import asyncio

from volue import mesh


async def async_print_version() -> None:
    async_connection = mesh.async_connection()
    # request version
    future = async_connection.get_version()
    # do some other work, until...
    # ... we actually need the version
    version_info = await future
    logging.info(version_info.full_version)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.
    
    logging.info("Synchronous get version: ")
    connection = mesh.connection()
    version_info = connection.get_version()
    logging.info(version_info.full_version)

    logging.info("Asynchronous get version: ")
    asyncio.run(async_print_version())

