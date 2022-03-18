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

    # The model to search in
    model = "SimpleThermalTestModel"

    # The Mesh object to start searching from
    start_object_path = "ThermalComponent"
    # OR
    # start_object_guid = uuid.UUID("0000000b-0001-0000-0000-000000000000")  # ThermalComponent

    # The query expressed using Mesh search language syntax
    # Traverse all children (*) of the start object, not case-sensitive ({}) and
    # accept all that has an attribute (.) called TsRawAtt
    query = "{*}.TsRawAtt"

    # Search for a time series attribute using this query
    reply = session.search_for_timeseries_attribute(model=model,
                                                    start_object_path=start_object_path,
                                                    query=query)

    # Close the remote session
    session.close()


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
