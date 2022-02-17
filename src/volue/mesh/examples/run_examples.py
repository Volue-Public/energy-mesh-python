from volue.mesh.examples import quickstart, _get_connection_info


def main(address, port, root_certificate_path):
    """Showing how to run examples."""

    # Run individual tests:
    quickstart.main(address, port, root_certificate_path)


if __name__ == "__main__":
    address, port, root_certificate_path = _get_connection_info()
    main(address, port, root_certificate_path)
