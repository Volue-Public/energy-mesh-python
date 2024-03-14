from datetime import datetime, timedelta

import helpers
from dateutil import tz

from volue.mesh import Connection, LinkRelationVersion, VersionedLinkRelationAttribute

OBJECT_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
ONE_TO_ONE_PATH = OBJECT_PATH + ".SimpleReference"
ONE_TO_MANY_PATH = OBJECT_PATH + ".PlantToChimneyRefCollection"
VERSIONED_ONE_TO_ONE_PATH = OBJECT_PATH + ".ReferenceSeriesAtt"
VERSIONED_ONE_TO_MANY_PATH = OBJECT_PATH + ".ReferenceSeriesCollectionAtt"


LOCAL_TIME_ZONE = tz.tzlocal()


def one_to_one_link_relation_example(session: Connection.Session):
    attribute_path = ONE_TO_ONE_PATH

    print("\nOne-to-one link relation")
    print("------------------------")

    # First read the attribute using `get_attribute`.
    # Full attribute information is needed to get target object type name.
    attribute = session.get_attribute(attribute_path, full_attribute_info=True)
    print(
        f"\tLink relation attribute points to {attribute.target_object_ids} of type {attribute.definition.target_object_type_name}"
    )

    # Get more information on the target object the link relation points to.
    # The link relation can be potentially nullable,check if there is any
    # target object the link relation points to.
    if len(attribute.target_object_ids) > 0:
        target_object = session.get_object(attribute.target_object_ids[0])
        print(f"\tTarget object path is: {target_object.path}")

    # Change the target object.
    new_target_object_path = OBJECT_PATH + ".PlantToChimneyRef/SomePowerPlantChimney1"
    new_target_object = session.get_object(new_target_object_path)
    session.update_link_relation_attribute(attribute, [new_target_object.id])

    # Read the updated attribute.
    attribute = session.get_attribute(attribute_path, full_attribute_info=True)
    print(f"\tUpdated link relation attribute points to {attribute.target_object_ids}")


def one_to_many_link_relation_example(session: Connection.Session):
    attribute_path = ONE_TO_MANY_PATH

    print("\nOne-to-many link relation")
    print("-------------------------")

    # First read the attribute using `get_attribute`.
    # Full attribute information is needed to get target object type name.
    attribute = session.get_attribute(attribute_path, full_attribute_info=True)
    print(
        f"\tLink relation attribute points to {attribute.target_object_ids} of type {attribute.definition.target_object_type_name}"
    )

    # Get more information on the target object the link relation points to.
    # The link relation can be potentially nullable,check if there is any
    # target object the link relation points to.
    print("\tTarget object paths:")
    for index, target_object_id in enumerate(attribute.target_object_ids, 1):
        target_object = session.get_object(target_object_id)
        print(f"\t{index}. {target_object.path}")

    # Remove all target objects.
    session.update_link_relation_attribute(attribute, [])

    # Read the updated attribute.
    attribute = session.get_attribute(attribute_path, full_attribute_info=True)
    print(f"\tUpdated link relation attribute points to {attribute.target_object_ids}")

    # Find target object for the new version.
    objects = session.search_for_objects(
        "Model/SimpleThermalTestModel",
        query=f"*[.Type={attribute.definition.target_object_type_name}&&.Name=SomePowerPlantChimney1]",
    )
    if len(objects) != 1:
        raise RuntimeError(
            f"invalid result from 'search_for_objects', "
            f"expected 1 target object, but got {len(objects)}"
        )
    new_target_object_1 = objects[0]

    # Set a new target object.
    # Updating one-to-many link relation without setting `append` flag will
    # replace all already existing target objects with the new ones.
    session.update_link_relation_attribute(attribute, [new_target_object_1.id])

    # Add a new target object.
    # Now use `append` flag to preserve already existing target objects.
    new_target_object_2_path = OBJECT_PATH + ".PlantToChimneyRef/SomePowerPlantChimney2"
    new_target_object_2 = session.get_object(new_target_object_2_path)
    session.update_link_relation_attribute(
        attribute, [new_target_object_2.id], append=True
    )

    # Read the updated attribute.
    attribute = session.get_attribute(attribute_path, full_attribute_info=True)
    print(f"\tUpdated link relation attribute points to {attribute.target_object_ids}")


def get_versioned_link_relation_attribute_information(
    attribute: VersionedLinkRelationAttribute, session: Connection.Session
):
    """Create a printable message from a versioned link relation attribute."""
    message = ""

    for entry_index, entry in enumerate(attribute.entries, 1):
        message += f"Entry {entry_index}\n"
        for version_index, version in enumerate(entry.versions, 1):
            target_object = session.get_object(version.target_object_id)

            valid_from_time_str = ""
            # If running on Windows and the datetime is before epoch
            # (1.1.1970 UTC) then we can't use `astimezone` because Windows
            # `localtime()` does not support it, see discussion:
            # https://bugs.python.org/issue31327
            if version.valid_from_time < datetime(1970, 1, 1, tzinfo=tz.UTC):
                # If the datetime is before 1.1.1970 UTC then print the time
                # zone info.
                valid_from_time_str = f"{version.valid_from_time:%Y-%m-%dT%H:%M:%S %Z}"
            else:
                # Otherwise convert to local time zone
                valid_from_time_str = (
                    f"{version.valid_from_time.astimezone(LOCAL_TIME_ZONE)}"
                )

            message += (
                f"\tVersion {version_index}. "
                f"target object name: {target_object.name}, "
                f"valid from time: {valid_from_time_str}\n"
            )

    return message


def versioned_one_to_one_link_relation_example(session: Connection.Session):
    attribute_path = VERSIONED_ONE_TO_ONE_PATH

    print("\nVersioned one-to-one link relation")
    print("----------------------------------")

    attribute = session.get_attribute(attribute_path)
    print(get_versioned_link_relation_attribute_information(attribute, session))

    # Remove the first version in entry.
    if len(attribute.entries) > 0 and len(attribute.entries[0].versions) > 0:
        session.update_versioned_link_relation_attribute(
            attribute_path,
            start_time=datetime.min,
            # Replacement interval end time is exclusive,
            # i.e.: <start_time, end_time).
            # That is why we need to add some small time fraction to make
            # sure the last version's `valid_from_time` is within the
            # replacement interval.
            end_time=attribute.entries[0].versions[0].valid_from_time
            + timedelta(microseconds=1),
            new_versions=[],
        )

    # Add a new version in entry.
    new_target_object_path = OBJECT_PATH + ".PlantToChimneyRef/SomePowerPlantChimney1"
    new_target_object = session.get_object(new_target_object_path)
    new_link_relation_version = LinkRelationVersion(
        target_object_id=new_target_object.id,
        # If no time zone is provided then it will be treated as UTC.
        valid_from_time=datetime(2022, 1, 1, tzinfo=LOCAL_TIME_ZONE),
    )

    session.update_versioned_link_relation_attribute(
        attribute_path,
        start_time=new_link_relation_version.valid_from_time,
        end_time=datetime.max,
        new_versions=[new_link_relation_version],
    )

    # Read the updated attribute.
    attribute = session.get_attribute(attribute_path)
    print("Updated link relation attribute:")
    print(get_versioned_link_relation_attribute_information(attribute, session))


def versioned_one_to_many_link_relation_example(session: Connection.Session):
    attribute_path = VERSIONED_ONE_TO_MANY_PATH

    print("\nVersioned one-to-many link relation")
    print("-----------------------------------")

    attribute = session.get_attribute(attribute_path)
    print(get_versioned_link_relation_attribute_information(attribute, session))

    print("Update of versioned one-to-many is not supported.")


def main(address, port, tls_root_cert):
    connection = Connection(address, port, tls_root_cert)
    with connection.create_session() as session:
        one_to_one_link_relation_example(session)
        one_to_many_link_relation_example(session)
        versioned_one_to_one_link_relation_example(session)
        versioned_one_to_many_link_relation_example(session)

        # to commit your changes you need to call:
        # session.commit()


if __name__ == "__main__":
    args = helpers.get_connection_info()
    main(*args)
