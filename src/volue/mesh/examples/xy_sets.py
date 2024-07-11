import datetime

import helpers

from volue import mesh

OBJECT_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
UNVERSIONED_PATH = OBJECT_PATH + ".XYSetAtt"
VERSIONED_PATH = OBJECT_PATH + ".XYZSeriesAtt"


def main(address, tls_root_pem_cert):
    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.Connection.insecure(address)

    with connection.create_session() as session:
        # In the default test model both the versioned and the unversioned
        # attribute are initially empty. The following two calls are therefore
        # expected to return [].

        print(f"Getting XY-sets from {UNVERSIONED_PATH}")
        xy_sets = session.get_xy_sets(UNVERSIONED_PATH)
        print(xy_sets)

        start_time = datetime.datetime.fromisoformat("1960-01-01")
        end_time = datetime.datetime.fromisoformat("2030-01-01")
        print(
            f"Getting XY-sets in interval [{start_time}, {end_time}) from {VERSIONED_PATH}"
        )
        xy_sets = session.get_xy_sets(VERSIONED_PATH, start_time, end_time)
        print(f"Received: {xy_sets}")

        sample_xy_set = mesh.XySet(
            None, [mesh.XyCurve(0.0, [(1.0, 10.3), (2.5, 15.9)])]
        )

        print(f"Updating XY-set at {UNVERSIONED_PATH}")
        session.update_xy_sets(UNVERSIONED_PATH, new_xy_sets=[sample_xy_set])
        print("Updated")

        print(
            f"Replacing XY-set versions in interval [{start_time}, {end_time}) with one version at {start_time}"
        )
        sample_xy_set.valid_from_time = start_time
        session.update_xy_sets(VERSIONED_PATH, start_time, end_time, [sample_xy_set])
        print("Updated")

        print(f"Getting XY-sets from {UNVERSIONED_PATH}")
        xy_sets = session.get_xy_sets(UNVERSIONED_PATH)
        print(f"Received: {xy_sets}")

        print(
            f"Getting XY-sets in interval [{start_time}, {end_time}) from {VERSIONED_PATH}"
        )
        xy_sets = session.get_xy_sets(VERSIONED_PATH, start_time, end_time)
        print(f"Received: {xy_sets}")


if __name__ == "__main__":
    args = helpers.get_connection_info()
    main(*args)
