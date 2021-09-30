from volue.mesh.examples.utility.print import get_connection_info
from volue.mesh.examples import quickstart


def main(address, port, secure_connection):
    """Showing how to run examples."""

    # Run individual tests:
    quickstart.main(address, port, secure_connection)


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    main(address, port, secure_connection)
