import argparse
import os
import uuid

from datetime import datetime
from typing import List

from volue.mesh import (AttributesFilter,
                        Connection,
                        LinkRelationAttribute,
                        LinkRelationVersion,
                        Object,
                        SimpleAttribute,
                        TimeseriesAttribute)


def main():
    parser = argparse.ArgumentParser(description="Fixup Mesh models as per the reorganization required by AuctionBidding")

    parser.add_argument("--keep-old-objects",
                        help="Whether to keep the old CurveOrders objects under Portfolios and Subportfolios. Default: True",
                        default=True)

    args = parser.parse_args()

    address, tls_root_pem_cert = get_connection_info(args.address, args.root_certificate_path)

    # For production environments create the connection using: with_tls, with_kerberos, or
    # with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure()

    with connection.create_session() as session:
        models = session.list_models()

        for model in models:
            fix_auction_bidding(model, session, args.keep_old_objects)


def get_connection_info():
    """Helper function to set hand over connection info to examples."""
    address = "localhost:50051"
    tls_root_pem_cert = ""

    if len(sys.argv) > 1:
        address = sys.argv[1]
    if len(sys.argv) > 2:
        root_certificate_path = sys.argv[2]
        if root_certificate_path:
            with open(root_certificate_path, "rb") as file:
                # In case multiple root certificates are needed, e.g.:
                # the same client accesses different Mesh servers (with different root certs)
                # Just combine into single file the root certificates, like:
                # -----BEGIN CERTIFICATE-----
                # ...(first certificate)...
                # -----END CERTIFICATE-----
                # -----BEGIN CERTIFICATE-----
                # ..(second certificate)..
                # -----END CERTIFICATE-----
                tls_root_pem_cert = file.read()

    return address, tls_root_pem_cert


def fix_auction_bidding(model: Object, session: Connection.Session, keep_old_objects: bool):
    query = "*[.Type=CurveOrders]"
    curve_orders_attr_names = ["MinVolume", "MaxVolume", "VolumeMin", "VolumeMax", "to_Areas"]
    curve_orders_attrs = AttributesFilter(name_mask=curve_orders_attr_names)

    # First, get all the CurveOrders objects in the model.
    for curve_orders_obj in session.search_for_objects(model,
                                                       query,
                                                       attributes_filter=curve_orders_attrs):
        # This is a bit ugly, since we're relying on the fact that objects' attributes are specified
        # with a dot in their path strings. The most "correct" way of grabbing the object's parent
        # (as opposed to the attribute which serves as its owner) would be to query Mesh using
        # 'get_attribute' to get the owner attribute and 'get_object' to get the attribute's owner
        # object, which is less efficient.
        parent_object_path = os.path.splitext(curve_orders_obj.owner_path)[0]

        has_auction_orders = "has_AuctionOrders"
        has_auction_orders_attr = AttributesFilter(name_mask=[has_auction_orders])

        parent = session.get_object(parent_object_path, attributes_filter=has_auction_orders_attr)

        # For each CurveOrders object, create a corresponding AuctionOrders object.
        auction_orders_obj = session.create_object(parent.attributes[has_auction_orders],
                                                   curve_orders_obj.name)

        set_curve_orders_obj_hierarchy(keep_old_objects)

        # Finally, set the values of the new AuctionOrders object to those of the corresponding
        # CurveOrders.
        for attr_name in curve_orders_attr_names:
            copy_attribute_values(session, auction_orders_obj, curve_orders_obj, attr_name)

    session.commit()


def set_curve_orders_obj_hierarchy():
    has_curve_orders = "has_CurveOrders"

    if keep_old_objects:
        new_curve_orders_obj = session.create_object(auction_orders_obj.attributes[has_curve_orders],
                                                     curve_orders_obj.name)

        # TODO: Copy the attributes of 'curve_orders_obj' to 'new_curve_orders_obj'. Depending
        # on the use case this may require cloning the CurveOrders' entire child object tree.
    else:
        # Set the new AuctionOrders object as the CurveOrders object's owner.
        has_curve_orders_attr = auction_orders_obj.attributes[has_curve_orders]

        session.update_object(curve_orders_obj.id, new_owner_attribute=has_curve_orders_attr)


def copy_attribute_values(session: Connection.Session,
                          auction_orders_obj: Object,
                          curve_orders_obj: Object,
                          attr_name: str):
    curve_orders_attr = curve_orders_obj.attributes[attr_name]
    auction_orders_attr = auction_orders_obj.attributes[attr_name]

    if isinstance(auction_orders_attr, SimpleAttribute):
        session.update_simple_attribute(auction_orders_attr, curve_orders_attr.value)
    elif isinstance(auction_orders_attr, TimeseriesAttribute):
        session.update_timeseries_attribute(auction_orders_attr,
                                            curve_orders_attr.expression,
                                            curve_orders_attr.time_series_resource.timeseries_key)
    elif isinstance(auction_orders_attr, LinkRelationAttribute):
        if curve_orders_attr.entries:
            # to_Areas should be a one-to-one link relation.
            assert len(curve_orders_attr.entries) == 1

            versions = curve_orders_attr.entries[0].versions

            if versions:
                target_object_id = find_current_target_object_id(versions)
                ids = [target_object_id] if target_object_id is not None else []

                session.update_link_relation_attribute(auction_orders_attr, ids)
    else:
        raise TypeError(f"Found attribute '{attr_name}' of unexpected type '{type(auction_orders_attr)}'")


# AuctionOrders.to_Areas is defined as a LinkRelationAttribute (i.e. ReferenceAttributeDefinition),
# whereas CurverOrders.to_Areas is a VersionedLinkRelationAttribute
# (i.e. ReferenceSeriesAttributeDefinition). In cases where CurveOrders.to_Areas has multiple
# versions (i.e. it points to different objects throughout time), we'll take the one corresponding
# to the current system time. Note that this assumes the system time is properly configured in the
# environment we're running this script on.
def find_current_target_object_id(versions: List[LinkRelationVersion]) -> uuid.UUID:
    tzinfo = versions[0].valid_from_time.tzinfo
    current_time = datetime.now(tzinfo)

    current_version = next(v for v in reversed(versions) if v.valid_from_time <= current_time)

    return current_version.target_object_id


if __name__ == "__main__":
    main()
