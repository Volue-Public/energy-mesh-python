import helpers

from volue.mesh import Connection, OwnershipRelationAttribute

leaves = []


def traverse_model_top_down(session: Connection.Session, target, depth=0):
    """Traverses the Mesh model recursively."""
    object = session.get_object(target)
    print(f"{'..' * depth}{object.name}")
    leaf = True

    for attr in object.attributes.values():
        if isinstance(attr, OwnershipRelationAttribute):
            for child_id in attr.target_object_ids:
                leaf = False
                traverse_model_top_down(session, child_id, depth + 1)
    if leaf:
        leaves.append(object)


def traverse_model_bottom_up(session: Connection.Session, target, model):
    object = session.get_object(target)
    depth = object.path.count("/") - 1
    print(f"{'..' * depth}{object.name}")
    if object.owner_id == model.id:
        print(model.name)
        return
    attribute = session.get_attribute(object.owner_id)
    traverse_model_bottom_up(session, attribute.owner_id, model)


def main(address, port, root_pem_certificate):
    """Showing how to traverse Mesh model."""
    connection = Connection(address, port, root_pem_certificate)

    with connection.create_session() as session:
        models = session.list_models()
        for model in models:
            leaves.clear()
            print(f"\nModel: '{model.name}'")
            print("Top-bottom traversal:")
            traverse_model_top_down(session, model.id)
            # Excepted output:
            # Model
            # ..ChildObject1
            # ....SubChildObject1
            # ....SubChildObject2
            # ..ChildObject2
            print("\nBottom-top traversal:")
            traverse_model_bottom_up(session, leaves[0].id, model)
            # Excepted output:
            # ....SubChildObject1
            # ..ChildObject1
            # Model


if __name__ == "__main__":
    address, port, root_pem_certificate = helpers.get_connection_info()
    main(address, port, root_pem_certificate)
