"""
Tests for volue.mesh.Object.
"""

import sys
import uuid

import grpc
import pytest
from volue.mesh import (
    AttributeBase,
    AttributesFilter,
    Object,
    OwnershipRelationAttribute,
)

from .test_utilities.utilities import AttributeForTesting, ObjectForTesting

OBJECT_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
OBJECT_ID = uuid.UUID("0000000A-0001-0000-0000-000000000000")


def verify_object_attributes(object: Object, full_info: bool = False):
    """Verifies all attributes of SomePowerPlant1 object."""
    assert len(object.attributes) >= 32

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
    # get object by path and ID
    targets = [OBJECT_PATH, OBJECT_ID]

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
def test_list_models(session):
    """
    Check that `list_models` list all existing models.
    """
    models = session.list_models()
    expected = ["SimpleThermalTestModel", "Utility"]
    model_names = [model.name for model in models]

    # there is no guarantee of order of the returned models
    assert sorted(model_names) == expected

    # check that each model
    for model in models:
        # has one attribute and it is an ownership relation attribute
        assert len(model.attributes) == 1
        assert isinstance(
            list(model.attributes.values())[0], OwnershipRelationAttribute
        )

        # does not have an owner
        assert model.owner_id is None
        assert model.owner_path is None

        # additionally check that other properties are set
        assert model.name is not None
        assert model.type_name is not None
        assert model.path is not None
        assert model.id is not None


@pytest.mark.database
def test_get_model_as_object(session):
    """
    Check that model (root object) can be read using `get_object`.
    """
    model_path = "Model/SimpleThermalTestModel"

    model = session.get_object(model_path, full_attribute_info=True)

    assert model.name == "SimpleThermalTestModel"
    assert model.type_name == "SimpleThermalTestRepository"
    assert model.path == model_path
    assert model.id is not None

    assert len(model.attributes) == 1
    assert isinstance(list(model.attributes.values())[0], OwnershipRelationAttribute)

    assert model.owner_id is None
    assert model.owner_path is None


@pytest.mark.database
def test_search_objects(session):
    """
    Check that `search_objects` returns correct objects according to specified search query.
    """
    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    start_object_id = uuid.UUID("0000000B-0001-0000-0000-000000000000")
    query = "*[.Type=ChimneyElementType]"

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
    object_to_update_id = uuid.UUID("0000000A-0005-0000-0000-000000000000")
    new_owner_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef/SomePowerPlantChimney1.ChimneyToChimneyRef"
    new_object_name = "SomeNewPowerPlantChimney"

    # ID is auto-generated when creating an attribute,
    # so first we need to read it.
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
    object_id = uuid.UUID("0000000A-0005-0000-0000-000000000000")

    # delete object by path and ID
    targets = [object_path, object_id]

    for target in targets:
        session.delete_object(target)
        with pytest.raises(grpc.RpcError, match="object not found:"):
            session.get_object(target)
        session.rollback()


@pytest.mark.database
def test_recursive_delete_object(session):
    """
    Check that `delete_object` deletes recursively existing object with children.
    """
    # delete object by path and ID
    targets = [OBJECT_PATH, OBJECT_ID]

    for target in targets:
        session.delete_object(target, recursive_delete=True)
        with pytest.raises(grpc.RpcError, match="object not found:"):
            session.get_object(target)
        session.rollback()


@pytest.mark.database
def test_delete_object_with_children_without_recursive_flag(session):
    """
    Check that `delete_object` will throw when trying to delete existing object
    with children without `recursive_delete` flag.
    """
    targets = [OBJECT_PATH, OBJECT_ID]

    for target in targets:
        with pytest.raises(grpc.RpcError, match="has child objects"):
            session.delete_object(target)


@pytest.mark.database
@pytest.mark.parametrize(
    "invalid_target",
    [
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef",
        "non_existing_path",
        uuid.uuid4(),
    ],
)
def test_object_apis_with_invalid_target(session, invalid_target):
    """
    Check that 'get_object', 'search_for_objects', 'update_object' and
    'delete_object' with invalid target (meaning incorrect object path or ID)
    will throw.
    """
    error_message_regex = "(not found)|(invalid type)"

    with pytest.raises(grpc.RpcError, match=error_message_regex):
        session.get_object(invalid_target)
    with pytest.raises(grpc.RpcError, match=error_message_regex):
        session.search_for_objects(invalid_target, "{*}.TsCalcAtt")
    with pytest.raises(grpc.RpcError, match=error_message_regex):
        session.update_object(invalid_target, new_name="new_name")
    with pytest.raises(grpc.RpcError, match=error_message_regex):
        session.delete_object(invalid_target)


@pytest.mark.server
def test_object_apis_with_attribute_as_target(session):
    """
    Check that 'get_object', 'search_for_objects', 'update_object' and
    'delete_object' with attribute as target will throw.
    """
    target = AttributeForTesting()
    error_message_regex = r"need to provide either path \(as str\), ID \(as uuid\.UUID\) or Mesh object instance"

    with pytest.raises(TypeError, match=error_message_regex):
        session.get_object(target)
    with pytest.raises(TypeError, match=error_message_regex):
        session.search_for_objects(target, "{*}.TsCalcAtt")
    with pytest.raises(TypeError, match=error_message_regex):
        session.update_object(target, new_name="new_name")
    with pytest.raises(TypeError, match=error_message_regex):
        session.delete_object(target)


@pytest.mark.database
@pytest.mark.parametrize(
    "invalid_target",
    [
        "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1",
        uuid.UUID("0000000A-0001-0000-0000-000000000000"),
        "Model/SimpleThermalTestModel/ThermalComponent",
        uuid.UUID("0000000B-0001-0000-0000-000000000000"),
        "non_existing_path",
        uuid.uuid4(),
    ],
)
def test_create_and_update_object_with_invalid_target(session, invalid_target):
    """
    Check that 'create_object' with invalid target (meaning incorrect owner
    attribute) and 'update_object' with invalid new owner attribute will throw.
    """
    error_message_regex = "(O|owner of the object not found)|(Wrong type of the owner)"

    with pytest.raises(grpc.RpcError, match=error_message_regex):
        session.create_object(invalid_target, "new_name")
    with pytest.raises(grpc.RpcError, match=error_message_regex):
        session.update_object(OBJECT_PATH, new_owner_attribute=invalid_target)


@pytest.mark.server
def test_create_and_update_object_with_attribute_as_target(session):
    """
    Check that 'create_object' with object as target and 'update_object' with
    new owner attribute as object will throw.
    """
    target = ObjectForTesting()

    with pytest.raises(
        TypeError,
        match=r"need to provide either path \(as str\), ID \(as uuid\.UUID\) or attribute instance",
    ):
        session.create_object(target, "new_name")
    with pytest.raises(TypeError, match="invalid new owner attribute"):
        session.update_object(OBJECT_PATH, new_owner_attribute=target)


@pytest.mark.asyncio
@pytest.mark.database
async def test_mesh_objects_async(async_session):
    """For async run the simplest test, implementation is the same."""

    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    query = "*[.Type=ChimneyElementType]"

    objects = await async_session.search_for_objects(start_object_path, query)
    assert len(objects) == 2
    assert all(isinstance(object, Object) for object in objects)

    new_object = await async_session.create_object(objects[0].owner_path, "new_object")
    assert isinstance(new_object, Object)

    new_name = "newer_object"
    await async_session.update_object(new_object.path, new_name)
    newer_object = await async_session.get_object(new_object.id)
    assert isinstance(newer_object, Object)
    assert newer_object.name == new_name

    await async_session.delete_object(newer_object.path)
    with pytest.raises(grpc.RpcError, match="object not found"):
        await async_session.get_object(newer_object.path)


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
