import sys


def get_connection_info():
    """Helper function to set hand over connection info to examples."""
    address = "localhost"
    port = 50051
    secure_connection = False

    if len(sys.argv) > 1:
        address = sys.argv[1]
        port = int(sys.argv[2])
        secure_connection = sys.argv[3] == "True"

    return address, port, secure_connection


