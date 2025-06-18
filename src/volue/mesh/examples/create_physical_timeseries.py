import helpers
import random
import string

from volue.mesh import Connection, Timeseries


def main(address, tls_root_pem_cert):
    """Showing how to create a physical time series resource."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        # Mesh will throw an exception if we try to create a time series with an existing path
        # and name. Add a random suffix to the time series name to avoid this.
        name_suffix = get_random_suffix()

        result = session.create_physical_timeseries(
            path="/Path/To/Test/Timeseries/",
            name="Test_Timeseries_" + name_suffix,
            curve_type=Timeseries.Curve.PIECEWISELINEAR,
            resolution=Timeseries.Resolution.HOUR,
            unit_of_measurement="cm",
        )

        session.commit()

        print(result)


def get_random_suffix() -> str:
    random_chars = 10

    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=random_chars)
    )


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
