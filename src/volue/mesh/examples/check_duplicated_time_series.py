#!/usr/bin/env python3

import uuid
from typing import Union

import helpers

from volue.mesh import Connection, TimeseriesAttribute


def get_pem_certificate_contents(certificate_path: str):
    """Reads the contents of a PEM certificate file."""

    tls_root_pem_cert = ""

    with open(certificate_path, "rb") as file:
        # In case multiple root certificates are needed, e.g.:
        # the same client accesses different Mesh servers (with different root certs)
        # Just combine into single file the root certificates, like:
        # -----BEGIN CERTIFICATE-----
        # ...(first certificate)...
        # -----END CERTIFICATE-----
        # -----BEGIN CERTIFICATE-----
        # ..(second certificate)..
        # -----END CERTIFICATE-----
        tls_root_pem_cert = file.read()

    return tls_root_pem_cert


def find_time_series_duplicates(
    session: Connection.Session, model: Union[str, uuid.UUID]
) -> dict[int, list[str]]:
    """
    Iterates over all Mesh model objects and stores time series key of physical
    or virtual time series connected to time series attributes.
    """
    time_series_info = {}

    for obj in session.search_for_objects(model, "{*}"):
        for attr in obj.attributes.values():
            if isinstance(attr, TimeseriesAttribute):
                if attr.time_series_resource is not None:
                    timeseries_key = attr.time_series_resource.timeseries_key
                    if timeseries_key not in time_series_info:
                        time_series_info[timeseries_key] = [attr.path]
                    else:
                        time_series_info[timeseries_key].append(attr.path)

    return time_series_info


def main(address, tls_root_pem_cert):
    """Checks for duplicated physical or virtual time series in a Mesh model."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    model_name = "SimpleThermalTestModel"

    with connection.create_session() as session:
        print(f"Model: '{model_name}'")
        time_series_info = find_time_series_duplicates(session, f"Model/{model_name}")

        for timeseries_key, paths in time_series_info.items():
            if len(paths) > 1:
                print(
                    f"Time series key {timeseries_key} is connected in {len(paths)} time series attributes:"
                )
                for path in paths:
                    print(f"  {path}")

    print("Check for duplicated time series done.")


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
