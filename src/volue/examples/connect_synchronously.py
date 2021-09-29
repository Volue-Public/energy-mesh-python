from volue.mesh import Connection
from volue.examples.utility.print import get_connection_info


def get_version(connection):
    # Sending a request to the server, want to know its version
    print("1. Requesting server version")
    version = connection.get_version()
    print(f"2. Server version is {version.version}")


def start_and_end_session(connection):
    print("A. Starting session")
    connection.open()
    print("B. Ending session")
    connection.close()


def main(address, port, secure_connection):
    # Creating a connection, but not sending any requests yet
    connection = Connection(address, port, secure_connection)
    get_version(connection)
    start_and_end_session(connection.create_session())


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    main(address, port, secure_connection)
    print("Done")

# Outputs:
# 1. Requesting server version
# 2. Server version is 1.12.5.0-dev
# A. Starting session
# B. Ending session
# Done
