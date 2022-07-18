"""
Tests for volue.mesh.Object.
"""

import sys

import grpc
import pytest

from volue.mesh import AttributeBase, AttributesFilter, Object

OBJECT_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"


def verify_object_attributes(object: Object, full_info: bool = False):
    """Verifies all attributes of SomePowerPlant1 object."""
    assert len(object.attributes) == 25

    for attribute in object.attributes.values():
        assert isinstance(attribute, AttributeBase)
        assert attribute.name is not None
        assert attribute.path is not None
        assert attribute.id is not None

        # without full info the definition is not set
        if full_info:
            assert attribute.definition is not None
        else:
            assert attribute.definition is None


@pytest.mark.database
def test_get_object(session):
    """
    Check that `get_object` returns specified object with
    all attributes and basic attribute information.
    """

    # ID is auto-generated when creating an object, so
    # first we need to read it.
    object_id = session.get_object(OBJECT_PATH).id

    # get object by path and ID
    targets = [OBJECT_PATH, object_id]

    for target in targets:
        object = session.get_object(target)
        assert isinstance(object, Object)
        assert object.name == "SomePowerPlant1"
        assert object.path == OBJECT_PATH
        assert object.type_name == "PlantElementType"
        assert (
            object.owner_path
            == "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
        )
        verify_object_attributes(object)


@pytest.mark.database
def test_get_object_with_full_attribute_info(session):
    """
    Check that `get_object` returns specified object with
    all attributes and full attribute information.
    """
    object = session.get_object(OBJECT_PATH, full_attribute_info=True)
    verify_object_attributes(object, full_info=True)

    # check one of the attributes
    assert (
        object.attributes["StringAtt"].definition.default_value
        == "Default string value"
    )


@pytest.mark.database
def test_get_object_with_attributes_filter_with_name_mask(session):
    """
    Check that `get_object` returns specified object with filtered attributes.
    """
    attributes_filter = AttributesFilter(name_mask=["StringAtt", "BoolArrayAtt"])
    object = session.get_object(OBJECT_PATH, attributes_filter=attributes_filter)

    assert len(object.attributes) == 2
    assert object.attributes["StringAtt"] is not None
    assert object.attributes["BoolArrayAtt"] is not None


@pytest.mark.database
def test_get_object_with_attributes_filter_with_non_existing_masks(session):
    """
    Check that `get_object` returns specified object with no attributes
    when non existing masks are used in attributes filter.
    """
    attributes_filter = AttributesFilter(namespace_mask=["NON_EXISTING"])

    object = session.get_object(OBJECT_PATH, attributes_filter=attributes_filter)
    assert len(object.attributes) == 0


@pytest.mark.database
def test_get_object_with_attributes_filter_with_return_no_attributes(session):
    """
    Check that `get_object` returns specified object with no attributes
    when `return_no_attributes` is set to True in attributes filter.
    """
    attributes_filter = AttributesFilter(return_no_attributes=True)

    object = session.get_object(OBJECT_PATH, attributes_filter=attributes_filter)
    assert len(object.attributes) == 0


@pytest.mark.database
def test_search_objects(session):
    """
    Check that `search_objects` returns correct objects according to specified search query.
    """
    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    query = "*[.Type=ChimneyElementType]"

    # ID is auto-generated when creating an object, so
    # first we need to read it.
    start_object_id = session.get_object(start_object_path).id

    # provide start object by path and ID
    targets = [start_object_path, start_object_id]

    for target in targets:
        objects = session.search_for_objects(target, query)
        assert len(objects) == 2

        for object in objects:
            assert isinstance(object, Object)
            assert (
                object.name == "SomePowerPlantChimney1"
                or object.name == "SomePowerPlantChimney2"
            )
            assert len(object.attributes) == 7


@pytest.mark.database
def test_create_object(session):
    """
    Check that `create_object` creates and returns new object.
    """
    owner_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef"
    new_object_name = "SomeNewPowerPlantChimney"

    # ID is auto-generated when creating an attribute, so
    # first we need to read it.
    owner_attribute_id = session.get_attribute(owner_attribute_path).id

    # provide owner attribute by path and ID
    targets = [owner_attribute_path, owner_attribute_id]

    for target in targets:
        new_object = session.create_object(target, new_object_name)
        assert isinstance(new_object, Object)
        assert new_object.name == new_object_name
        assert new_object.path == f"{owner_attribute_path}/{new_object_name}"

        object = session.get_object(new_object.id)
        assert new_object.name == object.name
        assert new_object.path == object.path
        assert new_object.type_name == object.type_name
        assert new_object.owner_id == object.owner_id
        assert new_object.owner_path == object.owner_path

        session.rollback()


@pytest.mark.database
def test_update_object(session):
    """
    Check that `update_object` updates existing object.
    """
    object_to_update_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef/SomePowerPlantChimney2"
    new_owner_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef/SomePowerPlantChimney1.ChimneyToChimneyRef"
    new_object_name = "SomeNewPowerPlantChimney"

    # ID is auto-generated when creating an object or attribute,
    # so first we need to read it.
    object_to_update_id = session.get_object(object_to_update_path).id
    new_owner_attribute_id = session.get_attribute(new_owner_attribute_path).id

    # update object by path and ID
    targets = [object_to_update_path, object_to_update_id]
    # provide new owner by path and ID
    new_owners = [new_owner_attribute_path, new_owner_attribute_id]

    for target in targets:
        for new_owner in new_owners:
            session.update_object(
                target,
                new_name=new_object_name,
                new_owner_attribute=new_owner,
            )

            new_object_path = f"{new_owner_attribute_path}/{new_object_name}"

            object = session.get_object(new_object_path)
            assert object.name == new_object_name
            assert object.path == new_object_path
            assert object.owner_path == new_owner_attribute_path

            session.rollback()


@pytest.mark.database
def test_delete_object(session):
    """
    Check that `delete_object` deletes existing object without children.
    """
    object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef/SomePowerPlantChimney2"

    # ID is auto-generated when creating an object, so
    # first we need to read it.
    object_id = session.get_object(object_path).id

    # delete object by path and ID
    targets = [object_path, object_id]

    for target in targets:
        session.delete_object(target)
        with pytest.raises(grpc.RpcError, match=r"Object not found:"):
            session.get_object(target)
        session.rollback()


@pytest.mark.database
def test_recursive_delete_object(session):
    """
    Check that `delete_object` deletes recursively existing object with children.
    """

    # ID is auto-generated when creating an object, so
    # first we need to read it.
    object_id = session.get_object(OBJECT_PATH).id

    # delete object by path and ID
    targets = [OBJECT_PATH, object_id]

    for target in targets:
        session.delete_object(target, recursive_delete=True)
        with pytest.raises(grpc.RpcError, match=r"Object not found:"):
            session.get_object(target)
        session.rollback()


@pytest.mark.asyncio
@pytest.mark.database
async def test_mesh_objects_async(async_session):
    """For async run the simplest test, implementation is the same."""

    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    query = "*[.Type=ChimneyElementType]"

    objects = await async_session.search_for_objects(start_object_path, query)
    assert len(objects) == 2

    test = objects[0].owner_path
    new_object = await async_session.create_object(objects[0].owner_path, "new_object")
    assert isinstance(new_object, Object)

    new_name = "newer_object"
    await async_session.update_object(new_object.path, new_name)
    newer_object = await async_session.get_object(new_object.id)
    assert isinstance(newer_object, Object)
    assert newer_object.name == new_name

    await async_session.delete_object(newer_object.path)
    with pytest.raises(grpc.RpcError, match=r"Object not found:"):
        await async_session.get_object(newer_object.path)


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
