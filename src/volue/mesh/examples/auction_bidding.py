import os

import helpers

from volue.mesh import (AttributesFilter,
                        Connection,
                        Object,
                        SimpleAttribute,
                        TimeseriesAttribute,
                        VersionedLinkRelationAttribute)


def main():
    address, tls_root_pem_cert = helpers.get_connection_info()

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        fix_auction_bidding(session)


def fix_auction_bidding(session: Connection.Session):
    target = "Model/DemoModel"
    query = "*[.Type=CurveOrders]"
    curve_orders_attr_names = ["MinVolume", "MaxVolume", "VolumeMin", "VolumeMax", "to_Areas"]
    curve_orders_attrs = AttributesFilter(name_mask=curve_orders_attr_names)

    # First, get all the CurveOrders objects in the model.
    for curve_orders_obj in session.search_for_objects(target,
                                                       query,
                                                       attributes_filter=curve_orders_attrs):
        # This is a bit ugly, since we're relying on the fact that objects' attributes are specified
        # with a dot in their path strings. The most "correct" way of grabbing the object's parent
        # (as opposed to the attribute which serves as its owner) would be to query Mesh using
        # 'get_attribute' to get the owner attribute and 'get_object' to get the attribute's owner
        # object, which is less efficient.
        print(curve_orders_obj)

        parent_object_path = os.path.splitext(curve_orders_obj.owner_path)[0]

        ownership_attr_name = "has_AuctionOrders"
        ownership_attr = AttributesFilter(name_mask=[ownership_attr_name])

        parent = session.get_object(parent_object_path, attributes_filter=ownership_attr)

        # For each CurveOrders object, create a corresponding AuctionOrders object and set it as the
        # CurveOrders object's owner.
        auction_orders_obj = session.create_object(parent.attributes[ownership_attr_name],
                                                   curve_orders_obj.name)

        curve_orders_ownership_attr = auction_orders_obj.attributes["has_CurveOrders"]

        session.update_object(curve_orders_obj.id, new_owner_attribute=curve_orders_ownership_attr)

        # Finally, set the values of the new AuctionOrders object to those of the corresponding
        # CurveOrders.
        for attr_name in curve_orders_attr_names:
            copy_attribute_values(session, auction_orders_obj, curve_orders_obj, attr_name)

    session.commit()


def copy_attribute_values(session: Connection.Session,
                          auction_orders_obj: Object,
                          curve_orders_obj: Object,
                          attr_name: str):
    curve_orders_attr = curve_orders_obj.attributes[attr_name]
    auction_orders_attr = auction_orders_obj.attributes[attr_name]

    print(curve_orders_attr)
    print(auction_orders_attr)

    if isinstance(auction_orders_attr, SimpleAttribute):
        session.update_simple_attribute(auction_orders_attr, curve_orders_attr.value)
    elif isinstance(auction_orders_attr, TimeseriesAttribute):
        session.update_timeseries_attribute(auction_orders_attr,
                                            curve_orders_attr.expression,
                                            curve_orders_attr.time_series_resource.timeseries_key)
    elif isinstance(auction_orders_attr, VersionedLinkRelationAttribute):
        session.update_versioned_one_to_many_link_relation_attribute(auction_orders_attr,
                                                                     curve_orders_attr.entries)
    else:
        raise TypeError(f"Found attribute '{attr_name}' of unexpected type '{type(auction_orders_attr)}'")


if __name__ == "__main__":
    main()
