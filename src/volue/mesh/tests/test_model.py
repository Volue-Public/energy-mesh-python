"""
Testing model, adding, removing, modifying objects.
"""

import sys
import time

import grpc
import pytest

THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH = (
    "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
)

TEST_PLANT_NAME = "TestPlant"
TEST_PLANT_NAME2 = "TestPlant2"
TEST_PLANT_NAME_PARENT = "TestPlantParent"
TEST_PLANT_NAME_CHILD = "TestPlantChild"


@pytest.mark.database
def test_two_sessions_adding_the_same_object(connection):

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    new_object1 = session1.create_object(
        THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME
    )
    new_object2 = session2.create_object(
        THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME
    )

    session1.commit()

    assert new_object1.name == TEST_PLANT_NAME

    time.sleep(1)

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

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    new_object1 = session1.create_object(
        THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME
    )
    session1.commit()

    assert new_object1.name == TEST_PLANT_NAME

    time.sleep(1)

    # expecting error
    with pytest.raises(
        grpc.RpcError,
        match="An element named "
        + TEST_PLANT_NAME
        + " already exists in the ThermalPowerToPlantRef element array",
    ):
        session2.create_object(
            THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME
        )

    # session2.commit() is not needed because session2.create_object should fail

    # clean up
    session1.delete_object(new_object1.id)
    session1.commit()

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_adding_different_objects(connection):

    with connection.create_session() as session1:
        new_object1 = session1.create_object(
            THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME
        )
        session1.commit()

        # check that object was created
        assert new_object1.name == TEST_PLANT_NAME

    with connection.create_session() as session2:

        new_object2 = session2.create_object(
            THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME2
        )
        session2.commit()

        # check that object was created
        assert new_object2.name == TEST_PLANT_NAME2

    # clean up
    with connection.create_session() as session3:
        session3.delete_object(new_object1.id)
        session3.delete_object(new_object2.id)
        session3.commit()


@pytest.mark.database
def test_two_sessions_adding_child_before_removing_parent(connection):

    with connection.create_session() as session1:

        # first create the parent object
        new_parent = session1.create_object(
            THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME_PARENT
        )
        session1.commit()

        # create child object
        new_child = session1.create_object(
            new_parent.attributes["SimpleOwnershipAtt"], TEST_PLANT_NAME_CHILD
        )
        session1.commit()

        # check that the objects are created
        assert new_parent.name == TEST_PLANT_NAME_PARENT
        assert new_child.name == TEST_PLANT_NAME_CHILD

    with connection.create_session() as session2:

        session2.delete_object(new_parent.id)

        # commit
        session2.commit()

        # check that parent object is deleted
        with pytest.raises(grpc.RpcError, match="object not found"):
            session2.get_object(new_parent.id)


@pytest.mark.database
def test_two_sessions_adding_child_after_removing_parent(connection):

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the parent object
    new_parent = session1.create_object(
        THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME_PARENT
    )
    session1.commit()

    # create child object
    session1.create_object(
        new_parent.attributes["SimpleOwnershipAtt"], TEST_PLANT_NAME_CHILD
    )

    time.sleep(1)

    session2.delete_object(new_parent.id)

    # commit the deletion of parent
    session2.commit()

    time.sleep(1)

    # commit on creation of child should fail
    with pytest.raises(grpc.RpcError, match="Missing owner"):
        session1.commit()

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_adding_child_after_removing_parent_and_commit(connection):

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the parent object
    new_parent = session1.create_object(
        THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME_PARENT
    )
    session1.commit()

    time.sleep(1)

    # delete parent object
    session2.delete_object(new_parent.id)

    # commit the deletion of parent
    session2.commit()

    # creation of child should fail

    with pytest.raises(grpc.RpcError, match="Owner of the object not found"):
        session1.create_object(
            new_parent.attributes["SimpleOwnershipAtt"], TEST_PLANT_NAME_CHILD
        )

    # commit on session1 is not needed because create should fail

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_removing_same_object_after_commit(connection):

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the object to be deleted
    new_object = session1.create_object(
        THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME
    )
    session1.commit()

    # deleting the object in session1
    session1.delete_object(new_object.id)
    session1.commit()

    time.sleep(1)

    # deleting the same object in session2 should fail
    with pytest.raises(grpc.RpcError, match="object not found"):
        session2.delete_object(new_object.id)

    # check that the new object is deleted
    with pytest.raises(grpc.RpcError, match="object not found"):
        session2.get_object(new_object.id)

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_removing_same_object(connection):

    session1 = connection.create_session()
    session1.open()

    session2 = connection.create_session()
    session2.open()

    # first create the object to be deleted
    new_object = session1.create_object(
        THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, TEST_PLANT_NAME
    )
    session1.commit()

    time.sleep(1)

    session1.delete_object(new_object.id)

    session2.delete_object(new_object.id)

    # commit on session1 should remove the object
    session1.commit()

    # Although intuitively we might think that commit on session2 should fail
    # because of object not existing anymore, but the actual behavior is that
    # it will ignore no longer existing objects meant to be deleted.
    session2.commit()

    session1.close()
    session2.close()


@pytest.mark.database
def test_two_sessions_updating_same_object_same_attribute(connection):

    object_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"

    with connection.create_session() as session1:

        # get object attributes info with session1
        object_s1 = session1.get_object(object_path)
        string_attribute_s1 = object_s1.attributes["StringAtt"]

        # update attribute
        session1.update_simple_attribute(string_attribute_s1, "session1 updated text")
        session1.commit()

        # check if attribute has a new value
        assert (
            session1.get_attribute(string_attribute_s1).value == "session1 updated text"
        )

    with connection.create_session() as session2:

        # get object attributes info with session2
        object_s2 = session2.get_object(object_path)
        string_attribute_s2 = object_s2.attributes["StringAtt"]

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
        object_s3 = session3.get_object(object_path)
        string_attribute_s3 = object_s3.attributes["StringAtt"]

        # update attribute to initial value
        session3.update_simple_attribute(string_attribute_s3, "Default string value")
        session3.commit()


@pytest.mark.database
def test_two_sessions_updating_same_object_different_attributes(connection):

    object_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"

    with connection.create_session() as session1:

        # get object attributes info with session1
        object_s1 = session1.get_object(object_path)
        int_attribute = object_s1.attributes["Int64Att"]

        # update attribute
        session1.update_simple_attribute(int_attribute, 100)
        session1.commit()

        # check if attribute has a new value
        assert session1.get_attribute(int_attribute).value == 100

    with connection.create_session() as session2:

        # get object attributes info with session2
        object_s2 = session2.get_object(object_path)
        string_attribute = object_s2.attributes["StringAtt"]

        # update attribute
        session2.update_simple_attribute(string_attribute, "updated string")
        session2.commit()

        # check if both attributes have new values
        int_attribute_s2 = object_s2.attributes["Int64Att"]
        assert session2.get_attribute(string_attribute).value == "updated string"
        assert session2.get_attribute(int_attribute_s2).value == 100

    # clean up
    with connection.create_session() as session3:

        # get object attributes info
        object_s3 = session3.get_object(object_path)
        string_attribute_s3 = object_s3.attributes["StringAtt"]
        int_attribute_s3 = object_s3.attributes["Int64Att"]

        # update attributes to initial values
        session3.update_simple_attribute(string_attribute_s3, "Default string value")
        session3.update_simple_attribute(int_attribute_s3, 64)
        session3.commit()


@pytest.mark.database
def test_two_sessions_updating_same_object_name(connection):

    test_object_name = "TestObject"
    session1_test_object_new_name = "Session1_TestObject_NewName"
    session2_test_object_new_name = "Session2_TestObject_NewName"

    with connection.create_session() as session1:
        # first create the test object
        new_object = session1.create_object(
            THERMAL_OBJECT_OWNERSHIP_RELATION_ATTRIBUTE_PATH, test_object_name
        )
        session1.commit()

        # check if object created with given name
        assert session1.get_object(new_object.id).name == test_object_name

        # update name in session1
        session1.update_object(new_object.id, new_name=session1_test_object_new_name)
        session1.commit()

        assert session1.get_object(new_object.id).name == session1_test_object_new_name

    with connection.create_session() as session2:

        # update name in session2
        session2.update_object(new_object.id, new_name=session2_test_object_new_name)
        session2.commit()

        assert session2.get_object(new_object.id).name == session2_test_object_new_name

    time.sleep(1)

    # check that current object name is as committed in session2
    with connection.create_session() as session3:
        assert session3.get_object(new_object.id).name == session2_test_object_new_name

    # clean up
    with connection.create_session() as session4:
        session4.delete_object(new_object.id)
        session4.commit()


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
