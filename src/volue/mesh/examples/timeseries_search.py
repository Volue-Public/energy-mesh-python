import helpers

from volue.mesh import Connection, OwnershipRelationAttribute, TimeseriesAttribute


def search_method_1(session: Connection.Session):
    """
    This method uses `search_for_timeseries_attributes` function.
    Wildcard search expression for attributes is not supported, meaning we
    can't get all time series attributes using simply "*" search expression.

    Useful e.g.: when searching for attributes with known names.
    """
    print("Search method 1")

    # Specify what you want to search for

    # The Mesh object to start searching from
    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    # OR
    # start_object_guid = uuid.UUID("0000000b-0001-0000-0000-000000000000")  # ThermalComponent

    # The query expressed using Mesh search language syntax
    # Traverse all children ({*}) of the start object and accept all that have
    # an attribute (.) called TsRawAtt
    query = "{*}.TsRawAtt"

    # Search for time series attributes using this query
    timeseries_attributes = session.search_for_timeseries_attributes(
        target=start_object_path, query=query
    )

    print(f"Number of found time series: {len(timeseries_attributes)}")
    for attribute in timeseries_attributes:
        if isinstance(attribute, TimeseriesAttribute):
            print(attribute.path)


def search_method_2(session: Connection.Session):
    """
    This method uses `search_for_objects` function with wildcard search
    expression ("*") that returns all objects.
    Useful when you want to traverse the complete model.

    Additionally here we show how to distinguish if time series attribute has
    a time series calculation expression defined or a physical time series
    connected to it.
    """
    print("Search method 2")

    # Provide root object (also referred to as a model) as the start object to
    # run the search.
    start_object_path = "Model/SimpleThermalTestModel"

    # Returns every object.
    query = "*"

    # Depending on the model size this may take long time to complete.
    objects = session.search_for_objects(target=start_object_path, query=query)

    print(f"Number of found objects: {len(objects)}")
    for object in objects:
        print(object.name)
        for attribute in object.attributes.values():
            if isinstance(attribute, TimeseriesAttribute):
                # If time series resource is set, then it means a physical
                # time series is connected to the attribute.
                if attribute.time_series_resource is not None:
                    print(
                        f"{attribute.path} has physical time series connected with time series key {attribute.time_series_resource.timeseries_key}"
                    )


def search_method_3(session: Connection.Session):
    """
    This method uses `get_object` function.
    Useful when you want to traverse a subset of the model tree from a given
    object.
    """
    print("Search method 3")

    def traverse_child_objects(session: Connection.Session, target):
        object = session.get_object(target, full_attribute_info=True)

        for attribute in object.attributes.values():
            if isinstance(attribute, OwnershipRelationAttribute):
                for child_id in attribute.target_object_ids:
                    traverse_child_objects(session, child_id)

            if isinstance(attribute, TimeseriesAttribute):
                print(attribute.path)

    object_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"
    traverse_child_objects(session, object_path)


def main(address, tls_root_pem_cert):
    """Showing how to search for Mesh time series attributes in various ways."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    # Create a remote session on the Volue Mesh server.
    with connection.create_session() as session:
        search_method_1(session)
        search_method_2(session)
        search_method_3(session)


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
