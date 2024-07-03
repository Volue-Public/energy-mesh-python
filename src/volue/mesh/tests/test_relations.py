"""
Tests for volue.mesh.LinkRelationVersion.
"""

import sys
from datetime import datetime, timedelta

import grpc
import pytest
from dateutil import tz

from volue.mesh import LinkRelationVersion
from volue.mesh.tests.test_utilities.utilities import CHIMNEY_1_ID, CHIMNEY_2_ID

ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME = "SimpleReference"
ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME = "PlantToChimneyRefCollection"
VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME = "ReferenceSeriesAtt"
VERSIONED_ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME = "ReferenceSeriesCollectionAtt"

ATTRIBUTE_PATH_PREFIX = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1."


def get_targets(session, attribute_name):
    """
    Return all possible targets for attribute APIs, like: ID or path.
    ID is always the first element in the returned target list.
    """
    # ID is auto-generated when creating an attribute, so
    # first we need to read it.
    attribute_path = ATTRIBUTE_PATH_PREFIX + attribute_name
    attribute = session.get_attribute(attribute_path)
    return [attribute.id, attribute_path, attribute]


@pytest.mark.database
def test_update_one_to_one_link_relation_attribute(session):
    """
    Check that updating one-to-one link relation attribute with new target
    object ID works.
    """
    targets = get_targets(session, ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME)
    new_target_object_ids = [CHIMNEY_1_ID]

    for target in targets:
        session.update_link_relation_attribute(
            target=target,
            new_target_object_ids=new_target_object_ids,
        )

        attribute = session.get_attribute(target)
        assert len(attribute.target_object_ids) == 1
        assert attribute.target_object_ids == new_target_object_ids

        session.rollback()


@pytest.mark.database
def test_update_one_to_one_link_relation_attribute_with_empty_target_object(session):
    """
    Check that updating one-to-one link relation attribute with empty new target
    object ID deletes current target object.
    """

    attribute_path = ATTRIBUTE_PATH_PREFIX + ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME

    session.update_link_relation_attribute(
        target=attribute_path,
        new_target_object_ids=[],
    )

    attribute = session.get_attribute(attribute_path)
    assert len(attribute.target_object_ids) == 0


@pytest.mark.database
def test_update_one_to_one_link_relation_attribute_invalid_input(session):
    attribute_path = ATTRIBUTE_PATH_PREFIX + ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME

    # `append` can't be used with one-to-one link relations
    with pytest.raises(
        grpc.RpcError, match="'append' must be false for one-to-one link relation"
    ):
        session.update_link_relation_attribute(
            target=attribute_path, new_target_object_ids=[], append=True
        )

    # there can't be more than 1 new target object ID used with one-to-one link relations
    with pytest.raises(grpc.RpcError, match="multiple target object IDs set"):
        session.update_link_relation_attribute(
            target=attribute_path, new_target_object_ids=[CHIMNEY_1_ID, CHIMNEY_2_ID]
        )


@pytest.mark.database
def test_update_one_to_many_link_relation_attribute(session):
    """
    Check that updating one-to-many link relation attribute with new target
    object IDs works.
    """
    targets = get_targets(session, ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME)
    new_target_object_ids = [CHIMNEY_1_ID, CHIMNEY_2_ID]

    for target in targets:
        # Because of lack of "free" chimneys to be added,
        # first lets remove all references.
        session.update_link_relation_attribute(
            target=target,
            new_target_object_ids=[],
        )

        session.update_link_relation_attribute(
            target=target,
            new_target_object_ids=new_target_object_ids,
        )

        attribute = session.get_attribute(target)
        assert len(attribute.target_object_ids) == 2

        # Check if both targets were found - the target object IDs are returned in
        # no particular order and it may change from one call to another.
        assert all(
            target_object_id in new_target_object_ids
            for target_object_id in attribute.target_object_ids
        )

        session.rollback()


@pytest.mark.database
def test_update_one_to_many_link_relation_attribute_with_empty_target_object(session):
    """
    Check that updating one-to-many link relation attribute with new target
    object IDs deletes current target objects.
    """
    attribute_path = ATTRIBUTE_PATH_PREFIX + ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME

    session.update_link_relation_attribute(
        target=attribute_path,
        new_target_object_ids=[],
    )

    attribute = session.get_attribute(attribute_path)
    assert len(attribute.target_object_ids) == 0


@pytest.mark.database
def test_update_one_to_many_link_relation_attribute_with_append_flag(session):
    """
    Check that updating one-to-many link relation attribute with `append`
    flag works.
    """
    attribute_path = ATTRIBUTE_PATH_PREFIX + ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME

    # Because of lack of "free" chimneys to be added,
    # first lets remove all references.
    session.update_link_relation_attribute(
        target=attribute_path,
        new_target_object_ids=[],
    )

    session.update_link_relation_attribute(
        target=attribute_path, new_target_object_ids=[CHIMNEY_2_ID], append=True
    )

    attribute = session.get_attribute(attribute_path)
    assert len(attribute.target_object_ids) == 1
    assert attribute.target_object_ids[0] == CHIMNEY_2_ID

    # Lets add another target object
    session.update_link_relation_attribute(
        target=attribute_path, new_target_object_ids=[CHIMNEY_1_ID], append=True
    )

    attribute = session.get_attribute(attribute_path)
    assert len(attribute.target_object_ids) == 2

    # Check if both targets were found - the target object IDs are returned in
    # no particular order and it may change from one call to another.
    assert all(
        target_object_id in [CHIMNEY_1_ID, CHIMNEY_2_ID]
        for target_object_id in attribute.target_object_ids
    )


@pytest.mark.database
def test_update_one_to_many_link_relation_attribute_with_append_flag_with_two_targets(
    session,
):
    """
    Check that updating one-to-many link relation attribute with `append`
    flag with multiple targets works.
    """
    attribute_path = ATTRIBUTE_PATH_PREFIX + ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME

    # Because of lack of "free" chimneys to be added,
    # first lets remove all references.
    session.update_link_relation_attribute(
        target=attribute_path,
        new_target_object_ids=[],
    )

    session.update_link_relation_attribute(
        target=attribute_path,
        new_target_object_ids=[CHIMNEY_1_ID, CHIMNEY_2_ID],
        append=True,
    )

    attribute = session.get_attribute(attribute_path)
    assert len(attribute.target_object_ids) == 2

    # Check if both targets were found - the target object IDs are returned in
    # no particular order and it may change from one call to another.
    assert all(
        target_object_id in [CHIMNEY_1_ID, CHIMNEY_2_ID]
        for target_object_id in attribute.target_object_ids
    )


@pytest.mark.database
def test_update_one_to_many_link_relation_attribute_with_invalid_input(
    session,
):
    attribute_path = ATTRIBUTE_PATH_PREFIX + ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME

    # If `append` flag is set the new_target_object_ids must not be empty.
    with pytest.raises(
        grpc.RpcError, match="'append' is set to true, but no target objects are set"
    ):
        session.update_link_relation_attribute(
            target=attribute_path, new_target_object_ids=[], append=True
        )


@pytest.mark.database
def test_update_versioned_one_to_one_link_relation_attribute_remove_one_version(
    session,
):
    # provide all possible attribute target types, like path or ID
    targets = get_targets(session, VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME)

    for target in targets:
        session.update_versioned_one_to_one_link_relation_attribute(
            target=target,
            start_time=datetime(2004, 1, 1),
            end_time=datetime(2014, 1, 1),
            new_versions=[],
        )

        attribute = session.get_attribute(target)

        assert len(attribute.entries) == 1

        entry = attribute.entries[0]
        assert len(entry.versions) == 2

        assert entry.versions[0].target_object_id == CHIMNEY_1_ID
        assert entry.versions[0].valid_from_time == datetime(2015, 6, 3, tzinfo=tz.UTC)

        assert entry.versions[1].valid_from_time == datetime(2017, 2, 1, tzinfo=tz.UTC)
        assert entry.versions[1].target_object_id == CHIMNEY_2_ID

        session.rollback()


@pytest.mark.database
def test_update_versioned_one_to_one_link_relation_attribute_remove_all_versions(
    session,
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    session.update_versioned_one_to_one_link_relation_attribute(
        target=attribute_path,
        start_time=datetime.min,
        end_time=datetime.max,
        new_versions=[],
    )

    attribute = session.get_attribute(attribute_path)

    assert len(attribute.entries) == 1
    assert len(attribute.entries[0].versions) == 0


@pytest.mark.database
@pytest.mark.parametrize(
    "new_version_valid_from_time, new_version_index",
    [
        (datetime(1990, 1, 1), 0),
        (datetime(2010, 1, 1), 1),
        (datetime(2016, 1, 2), 2),
        (datetime(2022, 1, 1), 3),
    ],
)
def test_update_versioned_one_to_one_link_relation_attribute_add_new_version(
    session, new_version_valid_from_time: datetime, new_version_index: int
):
    # We have too few chimneys in the existing test model to test various scenarios.
    # Create new test chimney.
    new_chimney_owner_attribute_path = ATTRIBUTE_PATH_PREFIX + "PlantToChimneyRef"
    new_chimney = session.create_object(
        new_chimney_owner_attribute_path,
        "SomeNewChimney",
    )

    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    new_versions = [LinkRelationVersion(new_chimney.id, new_version_valid_from_time)]

    # store already existing versions before the update
    old_versions = session.get_attribute(attribute_path).entries[0].versions

    session.update_versioned_one_to_one_link_relation_attribute(
        target=attribute_path,
        start_time=new_version_valid_from_time,
        end_time=new_version_valid_from_time + timedelta(microseconds=1),
        new_versions=new_versions,
    )

    attribute = session.get_attribute(attribute_path)

    assert len(attribute.entries) == 1

    entry = attribute.entries[0]
    assert len(entry.versions) == 4

    assert entry.versions[new_version_index].target_object_id == new_chimney.id
    # returned timestamps (including `valid_from_time`) are time-zone aware
    assert entry.versions[
        new_version_index
    ].valid_from_time == new_version_valid_from_time.replace(tzinfo=tz.UTC)

    # check that all old versions are still in place
    assert all(version in entry.versions for version in old_versions)


@pytest.mark.database
@pytest.mark.parametrize(
    "new_version_valid_from_time, new_version_index",
    [
        (datetime(2010, 1, 1), 1),
        (datetime(2016, 1, 2), 2),
        (datetime(2022, 1, 1), 3),
    ],
)
def test_update_versioned_one_to_one_link_relation_attribute_add_new_empty_version(
    session, new_version_valid_from_time: datetime, new_version_index: int
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    new_versions = [LinkRelationVersion(None, new_version_valid_from_time)]

    # store already existing versions before the update
    old_versions = session.get_attribute(attribute_path).entries[0].versions

    session.update_versioned_one_to_one_link_relation_attribute(
        target=attribute_path,
        start_time=new_version_valid_from_time,
        end_time=new_version_valid_from_time + timedelta(microseconds=1),
        new_versions=new_versions,
    )

    attribute = session.get_attribute(attribute_path)

    assert len(attribute.entries) == 1

    entry = attribute.entries[0]
    assert len(entry.versions) == 4

    assert entry.versions[new_version_index].target_object_id is None
    # returned timestamps (including `valid_from_time`) are time-zone aware
    assert entry.versions[
        new_version_index
    ].valid_from_time == new_version_valid_from_time.replace(tzinfo=tz.UTC)

    # check that all old versions are still in place
    assert all(version in entry.versions for version in old_versions)


@pytest.mark.database
@pytest.mark.parametrize(
    "start_time, end_time, new_version_index, versions_count",
    [
        (datetime(2005, 1, 1), datetime(2006, 1, 1), 0, 3),
        (datetime(2005, 1, 1), datetime(2016, 1, 1), 0, 2),
        (datetime(2005, 1, 1), datetime.max, 0, 1),
        (datetime(2015, 1, 1), datetime(2020, 1, 1), 1, 2),
        (datetime(2017, 1, 1), datetime.max, 2, 3),
        (datetime.min, datetime.max, 0, 1),
    ],
)
def test_update_versioned_one_to_one_link_relation_attribute_replace_versions(
    session,
    start_time: datetime,
    end_time: datetime,
    new_version_index: int,
    versions_count: int,
):
    # We have too few chimneys in the existing test model to test various scenarios.
    # Create new test chimney.
    new_chimney_owner_attribute_path = ATTRIBUTE_PATH_PREFIX + "PlantToChimneyRef"
    new_chimney = session.create_object(
        new_chimney_owner_attribute_path,
        "SomeNewChimney",
    )

    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    new_versions = [LinkRelationVersion(new_chimney.id, start_time)]

    session.update_versioned_one_to_one_link_relation_attribute(
        target=attribute_path,
        start_time=start_time,
        end_time=end_time,
        new_versions=new_versions,
    )

    attribute = session.get_attribute(attribute_path)

    assert len(attribute.entries) == 1

    entry = attribute.entries[0]
    assert len(entry.versions) == versions_count

    assert entry.versions[new_version_index].target_object_id == new_chimney.id
    # returned timestamps (including `valid_from_time`) are time-zone aware
    assert entry.versions[new_version_index].valid_from_time == start_time.replace(
        tzinfo=tz.UTC
    )


@pytest.mark.database
@pytest.mark.parametrize(
    "start_time, end_time, new_version_index, versions_count",
    [
        (datetime(2005, 1, 1), datetime(2006, 1, 1), 0, 3),
        (datetime(2005, 1, 1), datetime(2016, 1, 1), 0, 2),
        (datetime(2005, 1, 1), datetime.max, 0, 1),
        (datetime(2015, 1, 1), datetime(2020, 1, 1), 1, 2),
        (datetime(2017, 1, 1), datetime.max, 2, 3),
        (datetime.min, datetime.max, 0, 1),
    ],
)
def test_update_versioned_one_to_one_link_relation_attribute_replace_versions_with_empty_targets(
    session,
    start_time: datetime,
    end_time: datetime,
    new_version_index: int,
    versions_count: int,
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    new_versions = [LinkRelationVersion(None, start_time)]

    session.update_versioned_one_to_one_link_relation_attribute(
        target=attribute_path,
        start_time=start_time,
        end_time=end_time,
        new_versions=new_versions,
    )

    attribute = session.get_attribute(attribute_path)

    assert len(attribute.entries) == 1

    entry = attribute.entries[0]
    assert len(entry.versions) == versions_count

    assert entry.versions[new_version_index].target_object_id is None
    # returned timestamps (including `valid_from_time`) are time-zone aware
    assert entry.versions[new_version_index].valid_from_time == start_time.replace(
        tzinfo=tz.UTC
    )


@pytest.mark.database
def test_update_versioned_one_to_one_link_relation_attribute_with_invalid_interval(
    session,
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    with pytest.raises(
        grpc.RpcError,
        match="Interval .* is invalid",
    ):
        session.update_versioned_one_to_one_link_relation_attribute(
            target=attribute_path,
            start_time=datetime(2022, 1, 1),
            end_time=datetime(2021, 1, 1),
            new_versions=[LinkRelationVersion(CHIMNEY_1_ID, datetime(2022, 1, 1))],
        )


@pytest.mark.database
def test_update_versioned_one_to_one_link_relation_attribute_without_valid_from_time(
    session,
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    with pytest.raises(
        grpc.RpcError,
        match="each new link relation version must have a 'valid_from_time' timestamp",
    ):
        session.update_versioned_one_to_one_link_relation_attribute(
            target=attribute_path,
            start_time=datetime.min,
            end_time=datetime.max,
            new_versions=[LinkRelationVersion(CHIMNEY_1_ID, None)],
        )


@pytest.mark.database
def test_update_versioned_one_to_one_link_relation_attribute_with_valid_from_time_outside_of_interval(
    session,
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    with pytest.raises(
        grpc.RpcError,
        match="new link relations versions must be within the replacement interval",
    ):
        session.update_versioned_one_to_one_link_relation_attribute(
            target=attribute_path,
            start_time=datetime(2022, 1, 1),
            end_time=datetime.max,
            new_versions=[LinkRelationVersion(CHIMNEY_1_ID, datetime(2020, 1, 1))],
        )

    with pytest.raises(
        grpc.RpcError,
        match="new link relations versions must be within the replacement interval",
    ):
        session.update_versioned_one_to_one_link_relation_attribute(
            target=attribute_path,
            start_time=datetime.min,
            end_time=datetime(2022, 1, 1),
            new_versions=[LinkRelationVersion(CHIMNEY_1_ID, datetime(2022, 1, 1))],
        )


@pytest.mark.database
def test_update_versioned_one_to_many_link_relation_attribute(
    session,
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME
    )

    entry_1_version_1 = LinkRelationVersion(
        target_object_id=CHIMNEY_2_ID,
        valid_from_time=datetime(2022, 1, 1),
    )
    entry_1_version_2 = LinkRelationVersion(
        target_object_id=None,
        valid_from_time=datetime(2025, 1, 1),
    )
    entry_1_version_3 = LinkRelationVersion(
        target_object_id=CHIMNEY_2_ID,
        valid_from_time=datetime(2027, 1, 1),
    )
    entry1 = [entry_1_version_1, entry_1_version_2, entry_1_version_3]

    entry_2_version_1 = LinkRelationVersion(
        target_object_id=CHIMNEY_1_ID,
        valid_from_time=datetime(2000, 1, 1),
    )
    entry_2_version_2 = LinkRelationVersion(
        target_object_id=None,
        valid_from_time=datetime(2010, 1, 1),
    )
    entry2 = [entry_2_version_1, entry_2_version_2]

    new_entries = [entry1, entry2]
    session.update_versioned_one_to_many_link_relation_attribute(
        attribute_path, new_entries
    )

    attribute = session.get_attribute(attribute_path)

    assert len(attribute.entries) == 2

    for entry_index, new_entry in enumerate(new_entries):
        actual_entry = attribute.entries[entry_index]
        assert len(actual_entry.versions) == len(new_entry)

        for version_index, new_version in enumerate(new_entry):
            actual_version = attribute.entries[entry_index].versions[version_index]

            assert actual_version.target_object_id == new_version.target_object_id
            # returned timestamps (including `valid_from_time`) are time-zone aware
            assert (
                actual_version.valid_from_time
                == new_version.valid_from_time.replace(tzinfo=tz.UTC)
            )


@pytest.mark.database
def test_update_versioned_one_to_many_link_relation_attribute_remove_all_entries(
    session,
):
    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME
    )

    session.update_versioned_one_to_many_link_relation_attribute(attribute_path, [])

    attribute = session.get_attribute(attribute_path)
    assert len(attribute.entries) == 0


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_link_relations_async(async_session):
    """For async run the simplest test, implementation is the same."""

    attribute_path = ATTRIBUTE_PATH_PREFIX + ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    new_target_object_ids = [CHIMNEY_1_ID]

    await async_session.update_link_relation_attribute(
        target=attribute_path,
        new_target_object_ids=new_target_object_ids,
    )

    attribute = await async_session.get_attribute(attribute_path)
    assert len(attribute.target_object_ids) == 1
    assert attribute.target_object_ids == new_target_object_ids


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_versioned_one_to_one_link_relations_async(async_session):
    """For async run the simplest test, implementation is the same."""

    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_ONE_LINK_RELATION_ATTRIBUTE_NAME
    )

    await async_session.update_versioned_one_to_one_link_relation_attribute(
        target=attribute_path,
        start_time=datetime.min,
        end_time=datetime.max,
        new_versions=[],
    )

    attribute = await async_session.get_attribute(attribute_path)

    assert len(attribute.entries) == 1
    assert len(attribute.entries[0].versions) == 0


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_versioned_one_to_many_link_relations_async(async_session):
    """For async run the simplest test, implementation is the same."""

    attribute_path = (
        ATTRIBUTE_PATH_PREFIX + VERSIONED_ONE_TO_MANY_LINK_RELATION_ATTRIBUTE_NAME
    )

    await async_session.update_versioned_one_to_many_link_relation_attribute(
        target=attribute_path,
        new_entries=[],
    )

    attribute = await async_session.get_attribute(attribute_path)

    assert len(attribute.entries) == 0


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
