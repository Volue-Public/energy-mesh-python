import helpers

from volue.mesh import Connection, Timeseries


def main(address, port, root_pem_certificate):
    """Showing the quickest way to get started."""

    # Configure the connection you want
    connection = Connection(address, port, root_pem_certificate)

    # Which version is the server running
    version_info = connection.get_version()
    print(f"Connected to {version_info.name} {version_info.version}")

    # Create a remote session on the Volue Mesh server
    with connection.create_session() as session:
        print("You have now an open session and can request time series")

        result = session.create_physical_timeseries(
            path="/Path/To/Test/Timeseries/",
            name="Test_Timeseries",
            curve_type=Timeseries.Curve.PIECEWISELINEAR,
            resolution=Timeseries.Resolution.HOUR,
            unit_of_measurement="Unit1",
        )

        session.commit()

        print(result)


if __name__ == "__main__":
    address, port, root_pem_certificate = helpers.get_connection_info()
    main(address, port, root_pem_certificate)
