import helpers

from volue.mesh import Connection, OwnershipRelationAttribute, TimeseriesAttribute

keyword = "Income"
local_expressions = {}
template_expressions = {}


def search_calculation_expressions(session: Connection.Session, target):
    """
    Traverses the Mesh model recursively and finds all time series
    attributes that have calculation expressions containing specific string.
    """
    object = session.get_object(target, full_attribute_info=True)

    for attr in object.attributes.values():
        if isinstance(attr, OwnershipRelationAttribute):
            for child_id in attr.target_object_ids:
                search_calculation_expressions(session, child_id)
        elif isinstance(attr, TimeseriesAttribute):
            if keyword in attr.expression:
                # Local expression is set on attribute level.
                # Template expression is set on attribute definition level.
                # By default all attributes inherit template expression from
                # their attribute definition. If calculation expression is
                # changed explicitly for a given attribute, then it is called
                # a local expression.
                if attr.is_local_expression:
                    local_expressions[attr.path] = attr.expression
                else:
                    template_expressions[attr.definition.path] = attr.expression


def main(address, tls_root_pem_cert):

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        models = session.list_models()
        for model in models:
            print(f"\nModel: '{model.name}'")
            search_calculation_expressions(session, model.id)

            for path, expression in template_expressions.items():
                print(
                    f"Attribute definition path: {path} has template expression:\n{expression}"
                )

            for path, expression in local_expressions.items():
                print(f"Attribute path: {path} has local expression:\n{expression}")


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
