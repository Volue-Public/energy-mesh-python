import argparse
import os

import helpers

from volue.mesh import AttributesFilter, Connection


def main():
    parser = argparse.ArgumentParser(description='Example script for fixing up AuctionBidding models')

    parser.add_argument('model_name', help='Name of the model to fix')

    args = parser.parse_args()

    address, tls_root_pem_cert = helpers.get_connection_info()

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        fix_auction_bidding(args.model_name, session)


def fix_auction_bidding(model_name: str, session: Connection.Session):
    target = f"Model/{model_name}"
    query = "*[.Type=CurveOrders]"
    curve_orders_attribute_names = ["MinVolume", "MaxVolume", "VolumeMin", "VolumeMax"]
    curve_orders_attributes = AttributesFilter(name_mask=curve_orders_attribute_names)

    # First, get all the CurveOrders objects in the model.
    for curve_orders_obj in session.search_for_objects(target,
                                                       query,
                                                       attributes_filter=curve_orders_attributes):
        # This is a bit ugly, since we're relying on the fact that objects' attributes are specified
        # with a dot in their path strings. The most "correct" way of grabbing the object's parent
        # (as opposed to the attribute which serves as its owner) would be to query Mesh using
        # 'get_attribute' to get the owner attribute and 'get_object' to get the attribute's owner
        # object, which is less efficient.
        parent_object_path = os.path.splitext(curve_orders_obj.owner_path)[0]

        print(parent_object_path)

    #     ownership_attribute_name = "has_AuctionOrders"
    #     ownership_attribute = AttributesFilter(name_mask=[ownership_attribute_name])

    #     parent = session.get_object(parent_object_path, attributes_filter=ownership_attribute)

    #     # For each CurveOrders object, create a corresponding AuctionOrders object.
    #     auction_orders_obj = session.create_object(parent.attributes[ownership_attribute_name],
    #                                                curve_orders_obj.name)

    #     print(auction_orders_obj)

    #     # Finally, set the values of the new AuctionOrders object to those of the corresponding
    #     # CurveOrders.
    #     for attribute_name in curve_orders_attribute_names:
    #         curve_orders_attribute = curve_orders_obj.attributes[attribute_name]
    #         auction_orders_attribute = auction_orders_obj.attributes[attribute_name]

    #         print(curve_orders_attribute)
    #         print(auction_orders_attribute)

    #         session.update_simple_attribute(auction_orders_attribute, curve_orders_attribute.value)

    # session.commit()


if __name__ == "__main__":
    main()
