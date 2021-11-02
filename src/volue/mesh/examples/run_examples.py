from volue.mesh.examples import quickstart, _get_connection_info


def main(address, port, secure_connection):
    """Showing how to run examples."""

    # Run individual tests:
    quickstart.main(address, port, secure_connection)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)
