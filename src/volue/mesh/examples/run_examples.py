from volue.mesh.examples import quickstart, _get_connection_info


def main(address, port, root_pem_certificate):
    """Showing how to run examples."""

    # Run individual examples:
    quickstart.main(address, port, root_pem_certificate)


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
