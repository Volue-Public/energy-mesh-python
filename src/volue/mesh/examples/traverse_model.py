from volue.mesh import Connection, OwnershipRelationAttribute
from volue.mesh.examples import _get_connection_info


def add_new_objects_to_the_model(session: Connection.Session):
    target = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.ChimneyToChimneyRef"
    session.create_object(target, "SomeSubChimney1")
    session.create_object(target, "SomeSubChimney2")


def traverse_model(session: Connection.Session, target, depth=0):
    """Traverses the Mesh model recursively."""
    object = session.get_object(target, full_attribute_info=True)
    print(f"{'..' * depth}{object.name}")

    for attr in object.attributes.values():
        if isinstance(attr, OwnershipRelationAttribute):
            for child_id in attr.target_object_ids:
                traverse_model(session, child_id, depth + 1)


def main(address, port, root_pem_certificate):
    """Showing how to traverse Mesh model."""
    connection = Connection(address, port, root_pem_certificate)

    with connection.create_session() as session:
        # The basic model has 1 power plant that has 2 chimneys.
        # Add some objects to the model in this session to make
        # the example more attractive.
        add_new_objects_to_the_model(session)

        root_object = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"
        traverse_model(session, root_object)

        # Excepted output:
        # SomePowerPlant1
        # ..SomePowerPlantChimney2
        # ....SomeSubChimney1
        # ....SomeSubChimney2
        # ..SomePowerPlantChimney1


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
