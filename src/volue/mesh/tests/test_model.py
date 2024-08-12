# Testing model, adding, removing, modyfying objects.

import sys
import grpc
import pytest

TESTPLANT = "TestPlant"
TESTPLANT2 = "TestPlant2"
TESTPLANT_PARENT = "TestPlantParent"
TESTPLANT_CHILD = "TestPlantChild"


@pytest.mark.database
def test_two_sessions_adding_the_same_object(connection):

    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    root_object_ownership_relation_attribute = (
        f"{root_object_path}.ThermalPowerToPlantRef"
    )

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    new_object1 = session1.create_object(
        root_object_ownership_relation_attribute, TESTPLANT
    )
    new_object2 = session2.create_object(
        root_object_ownership_relation_attribute, TESTPLANT
    )

    session1.commit()

    assert new_object1.name == "TestPlant"

    # expecting error
    with pytest.raises(
        grpc.RpcError,
        match="session "
        + str(session2.session_id)
        + " is corrupt due to changes done by some other session, rollback your changes to fix your session",
    ):
        session2.commit()

    # clean up
    session1.delete_object(new_object1.id)
    session1.commit()

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_adding_the_same_object_after_commit(connection):

    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    root_object_ownership_relation_attribute = (
        f"{root_object_path}.ThermalPowerToPlantRef"
    )

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    new_object1 = session1.create_object(
        root_object_ownership_relation_attribute, TESTPLANT
    )
    session1.commit()

    assert new_object1.name == "TestPlant"

    # expecting error
    with pytest.raises(
        grpc.RpcError,
        match="An element named "
        + TESTPLANT
        + " already exists in the ThermalPowerToPlantRef element array",
    ):
        session2.create_object(root_object_ownership_relation_attribute, TESTPLANT)

    # session2.commit() is not needed because session2.create should fail

    # clean up
    session1.delete_object(new_object1.id)
    session1.commit()

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_adding_different_objects(connection):

    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    root_object_ownership_relation_attribute = (
        f"{root_object_path}.ThermalPowerToPlantRef"
    )

    with connection.create_session() as session1:
        new_object1 = session1.create_object(
            root_object_ownership_relation_attribute, TESTPLANT
        )

        # commit
        session1.commit()

        # check that object was created
        assert new_object1.name == "TestPlant"

    with connection.create_session() as session2:

        new_object2 = session2.create_object(
            root_object_ownership_relation_attribute, TESTPLANT2
        )

        # commit
        session2.commit()

        # check that object was created
        assert new_object2.name == "TestPlant2"

    # clean up
    with connection.create_session() as session3:
        session3.delete_object(new_object1.id)
        session3.delete_object(new_object2.id)
        session3.commit()


@pytest.mark.database
def test_two_sessions_adding_child_before_removing_parent(connection):

    root_object_ownership_relation_attribute_parent = (
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    )
    root_object_ownership_relation_attribute_child = f"{root_object_ownership_relation_attribute_parent}/TestPlantParent.SimpleOwnershipAtt"

    with connection.create_session() as session1:

        # first create the parent object
        new_parent = session1.create_object(
            root_object_ownership_relation_attribute_parent, TESTPLANT_PARENT
        )
        session1.commit()
        # create child object
        new_child = session1.create_object(
            root_object_ownership_relation_attribute_child, TESTPLANT_CHILD
        )
        session1.commit()

        # check that the objects are created
        assert new_parent.name == "TestPlantParent"
        assert new_child.name == "TestPlantChild"

    with connection.create_session() as session2:

        session2.delete_object(new_parent.id)

        # commit
        session2.commit()

        # check that parent object is deleted
        with pytest.raises(grpc.RpcError, match="Object not found"):
            session2.get_object(new_parent.id)


@pytest.mark.database
def test_two_sessions_adding_child_after_removing_parent(connection):

    root_object_ownership_relation_attribute_parent = (
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    )
    root_object_ownership_relation_attribute_child = f"{root_object_ownership_relation_attribute_parent}/TestPlantParent.SimpleOwnershipAtt"

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the parent object
    new_parent = session1.create_object(
        root_object_ownership_relation_attribute_parent, TESTPLANT_PARENT
    )
    session1.commit()

    # create child object
    new_child = session1.create_object(
        root_object_ownership_relation_attribute_child, TESTPLANT_CHILD
    )

    session2.delete_object(new_parent.id)

    # commit the deletion of parent
    session2.commit()

    # commit on creation of child should fail
    with pytest.raises(grpc.RpcError, match="Missing owner"):
        session1.commit()

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_adding_child_after_removing_parent_and_commit(connection):

    root_object_ownership_relation_attribute_parent = (
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    )
    root_object_ownership_relation_attribute_child = f"{root_object_ownership_relation_attribute_parent}/TestPlantParent.SimpleOwnershipAtt"

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the parent object
    new_parent = session1.create_object(
        root_object_ownership_relation_attribute_parent, TESTPLANT_PARENT
    )
    session1.commit()

    # delete parent object
    session2.delete_object(new_parent.id)

    # commit the deletion of parent
    session2.commit()

    # creation of child should fail

    with pytest.raises(grpc.RpcError, match="Owner of the object not found"):
        session1.create_object(
            root_object_ownership_relation_attribute_child, TESTPLANT_CHILD
        )

    # commit on session1 is not needed because create should fail

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_removing_same_object_after_commit(connection):

    root_object_ownership_relation_attribute = (
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    )

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the object to be deleted
    new_object = session1.create_object(
        root_object_ownership_relation_attribute, TESTPLANT
    )
    session1.commit()

    # deleting the object in session1
    session1.delete_object(new_object.id)
    session1.commit()

    # deleting the same object in session2 should fail
    with pytest.raises(grpc.RpcError, match="Object not found"):
        session2.delete_object(new_object.id)

    # check that the new object is deleted
    with pytest.raises(grpc.RpcError, match="Object not found"):
        session2.get_object(new_object.id)

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_removing_same_object(connection):

    root_object_ownership_relation_attribute = (
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    )

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the object to be deleted
    new_object = session1.create_object(
        root_object_ownership_relation_attribute, TESTPLANT
    )
    session1.commit()

    session1.delete_object(new_object.id)

    session2.delete_object(new_object.id)

    # commit on session1 should remove the object
    session1.commit()

    # commit on session2 should fail because of object not existing anymore - expected is "object not found"
    session2.commit()

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_updating_same_object_same_attribute(connection):

    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"

    with connection.create_session() as session1:

        # get object attributes info with session1
        root_object_full_info_s1 = session1.get_object(root_object_path)
        string_attribute_s1 = root_object_full_info_s1.attributes["StringAtt"]

        # update attribute
        session1.update_simple_attribute(string_attribute_s1, "session1 updated text")
        session1.commit()

        # check if attribute has a new value
        assert (
            session1.get_attribute(string_attribute_s1).value == "session1 updated text"
        )

    with connection.create_session() as session2:

        # get object attributes info with session2
        root_object_full_info_s2 = session2.get_object(root_object_path)
        string_attribute_s2 = root_object_full_info_s2.attributes["StringAtt"]

        # update attribute
        session2.update_simple_attribute(string_attribute_s2, "session2 updated text")
        session2.commit()

        # check if attribute has the newest value
        assert (
            session2.get_attribute(string_attribute_s2).value == "session2 updated text"
        )

    # clean up
    with connection.create_session() as session3:

        # get object attributes info
        root_object_full_info_s3 = session3.get_object(root_object_path)
        string_attribute_s3 = root_object_full_info_s3.attributes["StringAtt"]

        # update attribute to initial value
        session3.update_simple_attribute(string_attribute_s3, "Default string value")
        session3.commit()


@pytest.mark.database
def test_two_sessions_updating_same_object_different_attributes(connection):

    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"

    with connection.create_session() as session1:

        # get object attributes info with session1
        root_object_full_info_s1 = session1.get_object(root_object_path)
        int_attribute = root_object_full_info_s1.attributes["Int64Att"]

        # update attribute
        session1.update_simple_attribute(int_attribute, 100)
        session1.commit()

        # check if attribute has a new value
        assert session1.get_attribute(int_attribute).value == 100

    with connection.create_session() as session2:

        # get object attributes info with session2
        root_object_full_info_s2 = session2.get_object(root_object_path)
        string_attribute = root_object_full_info_s2.attributes["StringAtt"]

        # update attribute
        session2.update_simple_attribute(string_attribute, "updated string")
        session2.commit()

        # check if both attributes have new values
        int_attribute_s2 = root_object_full_info_s2.attributes["Int64Att"]
        assert session2.get_attribute(string_attribute).value == "updated string"
        assert session2.get_attribute(int_attribute_s2).value == 100

    # clean up
    with connection.create_session() as session3:

        # get object attributes info
        root_object_full_info_s3 = session3.get_object(root_object_path)
        string_attribute_s3 = root_object_full_info_s3.attributes["StringAtt"]
        int_attribute_s3 = root_object_full_info_s3.attributes["Int64Att"]

        # update attributes to initial values
        session3.update_simple_attribute(string_attribute_s3, "Default string value")
        session3.update_simple_attribute(int_attribute_s3, 64)
        session3.commit()


@pytest.mark.database
def test_two_sessions_updating_same_object_name(connection):

    test_object_ownership_relation_attribute = (
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    )

    with connection.create_session() as session1:
        # first create the test object
        new_object = session1.create_object(
            test_object_ownership_relation_attribute, "TestObject"
        )
        session1.commit()

        # check if object created with given name
        assert session1.get_object(new_object.id).name == "TestObject"

        # update name in session1
        session1.update_object(new_object.id, new_name="Session1_TestObject_NewName")
        session1.commit()

        assert session1.get_object(new_object.id).name == "Session1_TestObject_NewName"

    with connection.create_session() as session2:

        # update name in session2
        session2.update_object(new_object.id, new_name="Session2_TestObject_NewName")
        session2.commit()

        assert session2.get_object(new_object.id).name == "Session2_TestObject_NewName"

    # check that current object name is as committed in session2
    with connection.create_session() as session3:
        assert session3.get_object(new_object.id).name == "Session2_TestObject_NewName"

    # clean up
    with connection.create_session() as session4:
        session4.delete_object(new_object.id)
        session4.commit()


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
