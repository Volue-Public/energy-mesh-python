from volue.mesh.aio import Connection
from volue.mesh.examples.utility.print import get_connection_info

import asyncio


async def get_version(connection):
    # Sending a request to the server, want to know its version
    print("1. Requesting server version")
    version = await connection.get_version()
    print(f"2. Server version is {version.version}")


async def start_and_end_session(session):
    print("A. Starting session")
    await session.open()
    print("B. Ending session")
    await session.close()


async def main(address, port, secure_connection):
    # Creating a connection, but not sending any requests yet
    connection = Connection(address, port, secure_connection)
    # Indicate that these two functions can be run concurrently
    await asyncio.gather(
        get_version(connection),
        start_and_end_session(connection.create_session())
    )

if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    asyncio.run(main(address, port, secure_connection))
    print("Done")

# Outputs:
# 1. Requesting server version
# A. Starting session
# 2. Server version is 1.12.5.0-dev
# B. Ending session
# Done
