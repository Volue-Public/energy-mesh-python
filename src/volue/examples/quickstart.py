from volue.examples.utility.print import get_connection_info
from volue.mesh.connection import Connection


def main(address, port, secure_connection):
    # Configure the connection you want
    connection = Connection(address, port, secure_connection)
    # Which version is the server running
    mesh_server_version = connection.get_version()
    print(f"The connected Volue Mesh Server version is {mesh_server_version}")
    # Create a remote session on the Volue Mesh server
    connection.start_session()
    print("You have now a open session and can request timeseries")
    # Close the remote session
    connection.end_session()


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()

    main(address, port, secure_connection)
