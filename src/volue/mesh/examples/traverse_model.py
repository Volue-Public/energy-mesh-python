from volue.mesh import Connection, OwnershipRelationAttribute
from volue.mesh.examples import _get_connection_info


def traverse_model(session: Connection.Session, target, depth=0):
    """Traverses the Mesh model recursively."""
    object = session.get_object(target)
    print(f"{'..' * depth}{object.name}")

    for attr in object.attributes.values():
        if isinstance(attr, OwnershipRelationAttribute):
            for child_id in attr.target_object_ids:
                traverse_model(session, child_id, depth + 1)


def main(address, port, root_pem_certificate):
    """Showing how to traverse Mesh model."""
    connection = Connection(address, port, root_pem_certificate)

    with connection.create_session() as session:
        models = session.list_models()
        for model in models:
            traverse_model(session, model.id)

        # Excepted output:
        # Model
        # ..ChildObject1
        # ....SubChildObject1
        # ....SubChildObject2
        # ..ChildObject2


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
