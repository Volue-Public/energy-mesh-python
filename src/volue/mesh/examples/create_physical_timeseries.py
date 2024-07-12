import helpers

from volue.mesh import Connection, Timeseries


def main(address, port, root_pem_certificate):
    """Showing how to create a physical time series resource."""

    connection = Connection(address, port, root_pem_certificate)

    with connection.create_session() as session:
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
