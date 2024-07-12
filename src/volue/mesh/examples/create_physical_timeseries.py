import helpers

from volue.mesh import Connection, Timeseries


def main(address, tls_root_pem_cert):
    """Showing how to create a physical time series resource."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

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
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
