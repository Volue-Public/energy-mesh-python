from volue.mesh import Connection
from volue.mesh.examples.utility.print import get_connection_info


def get_version(connection):
    """Showing how to send get the server version."""
    print("1. Requesting server version")
    version = connection.get_version()
    print(f"2. Server version is {version.version}")


def start_and_end_session(session):
    """Showing how to start and end a session."""
    print("A. Starting session")
    session.open()
    print("B. Ending session")
    session.close()


def main(address, port, secure_connection):
    """Showing how to connect to a server and running two tasks sequentially."""
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
