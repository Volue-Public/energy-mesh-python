import sys
if len(sys.argv) > 1:
    address = sys.argv[1]
    port = int(sys.argv[2])
    secure_connection = sys.argv[3] == "True"


import asyncio
import volue.mesh


async def get_version(connection):
    # Sending a request to the server, want to know its version
    print("1. Requesting server version")
    version = await connection.get_version()
    print(f"2. Server version is {version.version}")


async def start_and_end_session(connection):
    print("A. Starting session")
    await connection.start_session()
    print("B. Ending session")
    await connection.end_session()


async def main():
    # Creating a connection, but not sending any requests yet
    connection = volue.mesh.AsyncConnection(address, port, secure_connection)
    # Indicate that these two functions can be run concurrently
    await asyncio.gather(
        get_version(connection),
        start_and_end_session(connection)
    )


asyncio.run(main())
print("Done")

# Outputs:
# 1. Requesting server version
# A. Starting session
# 2. Server version is 1.12.5.0-dev
# B. Ending session
# Done
