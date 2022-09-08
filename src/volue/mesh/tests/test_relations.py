"""
Tests for volue.mesh.LinkRelationVersion and volue.mesh.VersionedLinkRelationEntry.
"""

import sys
import uuid
from datetime import datetime

import grpc
import pytest

from volue.mesh import AttributeBase
from volue.mesh._attribute import LinkRelationAttribute

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
        assert attribute.target_object_ids[0] == new_target_object_ids[0]

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
    assert len(attribute.target_object_ids) == 1
    # Empty means it has target object ID set to
    # uuid.UUID("00000000-0000-0000-0000-000000000000").
    assert attribute.target_object_ids[0] == uuid.UUID(
        "00000000-0000-0000-0000-000000000000"
    )


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
    # TODO - fix it, currently all attributes with empty values
    # (e.g. empty collection attributes) are interpreted as AttributeBase,
    # so we can't use something like this:
    # assert len(attribute.target_object_ids) == 0
    assert isinstance(attribute, AttributeBase)
    assert not isinstance(attribute, LinkRelationAttribute)


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


# @pytest.mark.asyncio
# @pytest.mark.database
# async def test_update_link_relations_async(async_session):
#     """For async run the simplest test, implementation is the same."""

#     new_table = get_test_time_series_pyarrow_table()

#     attribute_path = TIME_SERIES_ATTRIBUTE_WITH_PHYSICAL_TIME_SERIES_PATH

#     await async_session.write_timeseries_points(
#         Timeseries(table=new_table, full_name=attribute_path)
#     )

#     reply_timeseries = await async_session.read_timeseries_points(
#         target=attribute_path,
#         start_time=TIME_SERIES_START_TIME,
#         end_time=TIME_SERIES_END_TIME,
#     )

#     assert new_table == reply_timeseries.arrow_table


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
