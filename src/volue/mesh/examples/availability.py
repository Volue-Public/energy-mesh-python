import uuid
from datetime import datetime

import helpers

from volue.mesh import Connection


def create_revision(session: Connection.Session):
    session.availability.create_revision(
        target="Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2",
        id="event_id",
        local_id="local_id",
        reason="reason",
    )


def main(address, tls_root_pem_cert):
    """Showing how to create a revision."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        create_revision(session)


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
