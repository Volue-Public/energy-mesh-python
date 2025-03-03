import uuid
from datetime import datetime

import helpers
import time
from volue.mesh import Connection


def read_timeseries_points(session: Connection.Session):
    """Showing how to read time series points."""
    
    start_time = time.time()
    
    # Define the time series identifier, it can be:
    # - time series key of a physical time series
    # - path of a time series attribute that is connected to a physical time series
    # - ID of a time series attribute that is connected to a physical time series
    timeseries_key = 3
    timeseries_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.TsRawAtt"
    timeseries_attribute_id = uuid.UUID("1EBD306B-3A5C-4C3F-B2BC-B4B2811DC139")

    # Defining a time interval to read time series from.
    # If no time zone is provided then it will be treated as UTC.
    start = datetime(2024, 1, 6, 6, 0, 0)
    end = datetime(2025, 3, 3, 8, 0, 0)

    # Each time series point occupies 20 bytes. By default gRPC has a limitation of 4MB inbound message size.
    # In case of larger data volumes please send request data in chunks.
    # E.g.: call multiple times `read_timeseries_points` with shorter interval.

    # Send request to read time series based on time series key.
    timeseries = session.read_timeseries_points(
        target=timeseries_attribute_id, start_time=start, end_time=end
    )

    timeseries = session.read_timeseries_points(
        target=uuid.UUID("9EA4441E-081A-4EB8-A203-99F98C2A7165"),
        start_time=start,
        end_time=end,
    )

    timeseries = session.read_timeseries_points(
        target=uuid.UUID("514E4B59-681E-4296-914A-E4F7D1F4E654"),
        start_time=start,
        end_time=end,
    )

    guid = [
        "E4AA787D-FB71-4377-9CDD-9A5CA64FF1F8",
        "627A6EAD-09A0-4F43-937E-63246E367AD5",
        "54DEACC9-57A8-44F1-ABC8-0C767913E986",
        "E1C8B45A-C3E8-4E0F-9E3B-593B5FA6B190",
        "511F63F9-DB52-410E-8D33-A5D256EF29D2",
        "0B93AF2A-D6F4-47AF-8D5F-52185FDE3A8C",
        "04588E20-7718-48FB-BB3B-5DAB3C6F970A",
        "DE07DDB2-FAFC-4082-B438-EA0E2DC9EC50",
        "F0E34401-731D-434E-800E-138C394C8482",
        "21FF3EF6-1678-41D5-BEB8-1901C4126FAF",
        "90C3DB66-CB68-4B0F-AE96-04F8D02F4C19",
        "3736A819-CD8C-4D4B-9F5E-EB532E637261",
        "07064529-CC49-49C8-AC0F-1C4509185507",
        "1EC96090-A2F2-4A9C-83A5-363C2E59F1DA",
        "E4AA787D-FB71-4377-9CDD-9A5CA64FF1F8",
        "514E4B59-681E-4296-914A-E4F7D1F4E654",
        "2F595958-D2AB-4BB2-A6F5-BE772877240D",
        "B732BD64-AA24-4B95-BCBA-E13F872F7FEB",
        "F2FE06F9-0A28-43F7-9090-13A9648BE8A4",
        "764089C7-886F-4447-9FB6-BEE538ECBAF1",
        "93DD9510-D752-496A-94B7-CD99B01241A2",
        "C0CF0948-4AC4-4079-B90D-662452372681",
        "FA68C226-43D9-4539-B9DA-692B95722BC1",
        "850651D8-BB65-42ED-B2CF-DEADB4409145",
        "17410152-E22A-4944-9D62-5698A292F5B0",
        "D0C6AC40-AD6D-4E02-A064-47244D12D325",
        "207A1568-19D3-4D42-BEB9-B37E9A44C12F",
        "E2756B78-686F-4EA4-9960-1DB782EAE618",
        "82A22A46-646D-46C7-B25D-09FD19789069",
        "8FB38290-255B-4422-9EE4-2A2388DE62D7",
        "514E4B59-681E-4296-914A-E4F7D1F4E654",
        "2F595958-D2AB-4BB2-A6F5-BE772877240D",
        "93DD9510-D752-496A-94B7-CD99B01241A2",
        "17410152-E22A-4944-9D62-5698A292F5B0",
        "C0EB183E-C8CB-4F02-BFE8-2E85952C0A76",
    ]

    for g in guid:
        timeseries = session.read_timeseries_points(
            target=uuid.UUID("514E4B59-681E-4296-914A-E4F7D1F4E654"),
            start_time=start,
            end_time=end,
        )

    print("%s" % (time.time() - start_time))
    # Send requests to read time series based on time series attribute path.
    # timeseries = session.read_timeseries_points(
    #     target=timeseries_attribute_id, start_time=start, end_time=end
    # )
    # print(
    #     f"Read {timeseries.number_of_points} points using time series attribute path."
    # )
    # print(timeseries.arrow_table.to_pandas())

    # Send requests to read time series based on time series attribute ID.
    # Attribute IDs are auto-generated when an object is created.
    # That is why we can't use any fixed ID in this example and the code is commented out.
    # timeseries = session.read_timeseries_points(
    #     target=timeseries_attribute_id, start_time=start, end_time=end
    # )
    # print(f"Read {timeseries.number_of_points} points using time series attribute ID.")
    # print(timeseries.arrow_table.to_pandas())


def main(address, tls_root_pem_cert):
    """Showing how to get time series points."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    for _ in range(20000):
        connection = Connection.insecure(address)

        with connection.create_session() as session:
            read_timeseries_points(session)


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
