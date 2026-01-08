import helpers

from volue.mesh import AttributesFilter, Connection, OwnershipRelationAttribute


def main(address, tls_root_pem_cert):
    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent"

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        # Root object has an ownership relation attribute that point to objects
        # of "PlantElementType" type. We want to add new object of this type.
        root_object = session.get_object(root_object_path, full_attribute_info=True)

        # First get the ownership attribute:
        # If we know the name of the attribute we can use:
        ownership_relation_attribute = root_object.attributes["ThermalPowerToPlantRef"]

        # If we don't know the name, but only the type of the target object
        # (the object it points to):
        # Note: This requires `full_attribute_info` flag set to True when
        #       calling `get_object` or `get_attribute`.
        for attribute in root_object.attributes.values():
            if (
                isinstance(attribute, OwnershipRelationAttribute)
                and attribute.definition.target_object_type_name == "PlantElementType"
            ):
                ownership_relation_attribute = attribute

        new_object = session.create_object(
            ownership_relation_attribute, "SomeNewPowerPlant"
        )
        print(f"New object created: {new_object.path}")

        int_attribute = new_object.attributes["Int64Att"]

        # Object returned by `create_object` contains all attributes with basic
        # information.
        print("One of the new object's attributes (basic information):")
        print(int_attribute)

        # Now let's update attribute's value.
        session.update_simple_attribute(int_attribute, 100)

        # Check updated value, but this time get also more information like
        # attribute definition. Use either:
        # - `get_object` with `full_attribute_info` flag
        # - `get_attribute` with `full_attribute_info` flag
        attribute_with_full_info = session.get_attribute(
            int_attribute, full_attribute_info=True
        )
        print("One of the new object's attributes (full information):")
        print(attribute_with_full_info)

        # We can also filter attributes by e.g. name.
        object_with_filtered_attributes = session.get_object(
            new_object,
            attributes_filter=AttributesFilter(name_mask=["DblAtt", "StringAtt"]),
        )
        print(
            f"Filtered attributes count: {len(object_with_filtered_attributes.attributes)}"
        )

        # Connect a time series resource to a time series attribute of the new object.
        new_timeseries_resource_key = 2
        session.update_timeseries_attribute(
            new_object.attributes["TsRawAtt"],
            new_timeseries_resource_key=new_timeseries_resource_key,
        )

        # Now disconnect the time series resource. Set `new_timeseries_resource_key`
        # to 0 to disconnect.
        session.update_timeseries_attribute(
            new_object.attributes["TsRawAtt"],
            new_timeseries_resource_key=0,
        )

        # Change local expression of a time series attribute of the new object.
        # The local expression is not validated during update operation.
        # Invalid local expressions will be accepted but will cause failures
        # when reading time series points later. Before committing changes,
        # make sure the expression is valid, by reading time series points and
        # verifying they are as expected.
        new_local_expression = "## = 2\n"
        session.update_timeseries_attribute(
            new_object.attributes["TsCalcAtt"],
            new_local_expression=new_local_expression,
        )

        # We can also update the template expression of a time series attribute definition,
        # which affects all attribute instances using that definition.
        ts_calc_attribute = session.get_timeseries_attribute(
            new_object.attributes["TsCalcAtt"], full_attribute_info=True
        )
        # The template expression is not validated during update operation.
        # Invalid template expressions will be accepted but will cause failures
        # when reading time series points later - if there is no local
        # expression set that takes precedence. In such case, before committing
        # changes, make sure the expression is valid, by reading time series
        # points and verifying they are as expected.
        new_template_expression = "## = 100\n"
        session.update_timeseries_attribute_definition(
            ts_calc_attribute.definition,
            new_template_expression=new_template_expression,
        )
        # Note: Updating the template expression affects ALL attributes that use
        # this definition across all objects in the model (unless they have a
        # local expression override).

        # Now lets change the object name.
        session.update_object(new_object, new_name="NewNamePowerPlant")
        print("Object's name changed.")

        # Delete the updated object.
        # Because we changed object's name, we can't provide old `Object`
        # instance as it is still having the old object name.
        # Use object's ID instead or provide the path to the object explicitly.
        session.delete_object(new_object.id)
        print("Object deleted.")

        # To commit your changes you need to call:
        # session.commit()


if __name__ == "__main__":
    args = helpers.get_connection_info()
    main(*args)
