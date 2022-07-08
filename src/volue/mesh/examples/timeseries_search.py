from volue.mesh.examples import _get_connection_info
from volue.mesh import Connection


def main(address, port, root_pem_certificate):
    """Showing how to search for mesh object that returns a time series."""

    # Configure the connection you want
    connection = Connection(address, port, root_pem_certificate)

    # Create a remote session on the Volue Mesh server
    session = connection.create_session()
    session.open()

    ###
    # Specify what you want to search for
    ###

    # The Mesh object to start searching from
    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    # OR
    # start_object_guid = uuid.UUID("0000000b-0001-0000-0000-000000000000")  # ThermalComponent

    # The query expressed using Mesh search language syntax
    # Traverse all children (*) of the start object, not case-sensitive ({}) and
    # accept all that has an attribute (.) called TsRawAtt
    query = "{*}.TsRawAtt"

    # Search for time series attributes using this query
    timeseries_attributes = session.search_for_timeseries_attributes(
        target=start_object_path,
        query=query)

    print(f'Number of found time series: {len(timeseries_attributes)}')

    # Close the remote session
    session.close()


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
