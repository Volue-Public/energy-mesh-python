from volue.mesh.examples import _get_connection_info
from volue.mesh import Connection


def main(address, port, secure_connection):
    """Showing the quickest way to get started."""

    # Configure the connection you want
    connection = Connection(address, port, secure_connection)

    # Which version is the server running
    mesh_server_version = connection.get_version()
    print(f"The connected Volue Mesh Server is {mesh_server_version}")

    # Create a remote session on the Volue Mesh server
    session = connection.create_session()
    session.open()
    print("You have now an open session and can request timeseries")

    # Close the remote session
    session.close()


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)