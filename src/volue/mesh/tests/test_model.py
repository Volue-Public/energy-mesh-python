"""
Testing model, adding, removing, modyfying objects
"""

import asyncio
import sys
from time import sleep

import grpc
import pytest

# After this timeout an inactive session must be closed by the server.
# gRPC session timeout + ping interval + minimal margin:
# 5 mins + 1 min + 1 sec
SESSION_LIFETIME_EXTENSION_TESTS_SLEEP_VALUE_IN_SECS = 361


@pytest.mark.database
def test_two_sessions_adding_same_object(connection):
    
    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    root_object_ownership_relation_attribute = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    
    session1 = connection.create_session()
    session1.open()
  
    session2 = connection.create_session()
    session2.open()
   
    session1.create_object(root_object_ownership_relation_attribute,"TestPlant")
    session2.create_object(root_object_ownership_relation_attribute,"TestPlant")
    
    session1.commit()

    new_object_path = f"{root_object_path}/{'TestPlant'}"
    root_object_full_info = session1.get_object(new_object_path, full_attribute_info=True)
    assert root_object_full_info.name == 'TestPlant'

    # expecting error
    with pytest.raises(grpc.RpcError, match="session "+str(session2.session_id)+" is corrupt due to changes done by some other session, rollback your changes to fix your session"):
        session2.commit()

    #clean up
    new_object_id = session1.get_object(new_object_path).id
    session1.delete_object(new_object_id)
    session1.commit()

    session1.close()
    session2.close()
    
    
@pytest.mark.database
def test_two_sessions_adding_same_object2(connection):
     
    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    root_object_ownership_relation_attribute = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    
    session1 = connection.create_session()
    session1.open()
  
    session2 = connection.create_session()
    session2.open()
   
    session1.create_object(root_object_ownership_relation_attribute,"TestPlant2")
    session1.commit()
    
    new_object_path = f"{root_object_path}/{'TestPlant2'}"
    root_object_full_info = session1.get_object(new_object_path, full_attribute_info=True)
    assert root_object_full_info.name == 'TestPlant2'
    
    # expecting error
    with pytest.raises(grpc.RpcError, match="An element named TestPlant2 already exists in the ThermalPowerToPlantRef element array"):
        session2.create_object(root_object_ownership_relation_attribute,"TestPlant2")
    
    #session2.commit() is not needed because session2.create should fail

    #clean up
    new_object_id = session2.get_object(new_object_path).id
    session1.delete_object(new_object_id)
    session1.commit()

    session1.close()
    session2.close() 
    
   
@pytest.mark.database
def test_two_sessions_adding_different_objects(connection):
    
    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    root_object_ownership_relation_attribute = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"

    with connection.create_session() as session1:
            session1.create_object(root_object_ownership_relation_attribute,"TestPlant_1")
            
            # commit
            session1.commit()

            # check that object was created
            new_object_path1 = f"{root_object_path}/{'TestPlant_1'}"
            root_object_full_info = session1.get_object(new_object_path1, full_attribute_info=True)
            assert root_object_full_info.name == 'TestPlant_1'

    with connection.create_session() as session2:
        
            session2.create_object(root_object_ownership_relation_attribute,"TestPlant_2")
          
            # commit
            session2.commit()

            # check that object was created
            new_object_path2 = f"{root_object_path}/{'TestPlant_2'}"
            root_object_full_info = session2.get_object(new_object_path2, full_attribute_info=True)
            assert root_object_full_info.name == 'TestPlant_2'

    #clean up
    with connection.create_session() as session3:
            new_object_path1 = f"{root_object_path}/{'TestPlant_1'}"  
            new_object_path2 = f"{root_object_path}/{'TestPlant_2'}"
            new_object_id1 = session3.get_object(new_object_path1).id
            session3.delete_object(new_object_id1)
            new_object_id2 = session3.get_object(new_object_path2).id
            session3.delete_object(new_object_id2)
            session3.commit()

 
@pytest.mark.database
def test_two_sessions_adding_child_before_removing_parent(connection):
      
    root_object_ownership_relation_attribute_parent = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    root_object_ownership_relation_attribute_child = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/TestPlantParent.SimpleOwnershipAtt"
    
    with connection.create_session() as session1:
    
            #first create the parent object
            session1.create_object(root_object_ownership_relation_attribute_parent,"TestPlantParent")
            session1.commit()
            # create child object
            session1.create_object(root_object_ownership_relation_attribute_child,"TestPlantChild")
            session1.commit()
            
            # check that the objects are created
            parent_object_path = f"{root_object_ownership_relation_attribute_parent}/{'TestPlantParent'}"
            parent_object_full_info = session1.get_object(parent_object_path, full_attribute_info=True)
            assert parent_object_full_info.name == 'TestPlantParent'
            
            child_object_path = f"{root_object_ownership_relation_attribute_child}/{'TestPlantChild'}"
            child_object_full_info = session1.get_object(child_object_path, full_attribute_info=True)
            assert child_object_full_info.name == 'TestPlantChild'

    with connection.create_session() as session2:
        
            parent_object_path = f"{root_object_ownership_relation_attribute_parent}/{'TestPlantParent'}"
    
            parent_object_id = session2.get_object(parent_object_path).id
            session2.delete_object(parent_object_id)
            # commit
            session2.commit()

            # check that parent object is deleted
            with pytest.raises(grpc.RpcError, match="Object not found"):
                parent_object_full_info = session2.get_object(parent_object_path, full_attribute_info=True)
                
        
@pytest.mark.database
def test_two_sessions_adding_child_after_removing_parent(connection):
        
    root_object_ownership_relation_attribute_parent = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    root_object_ownership_relation_attribute_child = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/TestPlantParent.SimpleOwnershipAtt"
        
    session1 = connection.create_session()
    session1.open()
  
    session2 = connection.create_session()
    session2.open()
   
    #first create the parent object
    session1.create_object(root_object_ownership_relation_attribute_parent,"TestPlantParent")
    session1.commit()
    # create child object
    session1.create_object(root_object_ownership_relation_attribute_child,"TestPlantChild")
    
    #delete parent object    
    parent_object_path = f"{root_object_ownership_relation_attribute_parent}/{'TestPlantParent'}"
    
    parent_object_id = session2.get_object(parent_object_path).id
    session2.delete_object(parent_object_id)
    
    # commit the deletion of parent
    session2.commit()
    
    # commit on creation of child should fail
    with pytest.raises(grpc.RpcError, match="Missing owner"):
        session1.commit()  
   
    session1.close()
    session2.close()
    
        
@pytest.mark.database
def test_two_sessions_adding_child_after_removing_parent2(connection):
     
    root_object_ownership_relation_attribute_parent = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    root_object_ownership_relation_attribute_child = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/TestPlantParent.SimpleOwnershipAtt"
        
    session1 = connection.create_session()
    session1.open()
  
    session2 = connection.create_session()
    session2.open()
   
    #first create the parent objectd
    session1.create_object(root_object_ownership_relation_attribute_parent,"TestPlantParent")
    session1.commit()
    
    #delete parent object    
    parent_object_path = f"{root_object_ownership_relation_attribute_parent}/{'TestPlantParent'}"
    
    parent_object_id = session2.get_object(parent_object_path).id
    session2.delete_object(parent_object_id)
    
    # commit the deletion of parent
    session2.commit()
    
    # commit on creation of child should fail
    
    with pytest.raises(grpc.RpcError, match="Owner of the object not found"):
        session1.create_object(root_object_ownership_relation_attribute_child,"TestPlantChild")
    
    #commit on session1 is not needed because create should fail
    
    session1.close()
    session2.close()

    
@pytest.mark.database
def test_two_sessions_removing_same_object(connection):
    
    root_object_ownership_relation_attribute = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    #root_object_ownership_relation_attribute_child = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/TestPlantParent.SimpleOwnershipAtt"
        
    session1 = connection.create_session()
    session1.open()
  
    session2 = connection.create_session()
    session2.open()
   
    #first create the object to be deleted
    session1.create_object(root_object_ownership_relation_attribute,"TestPlantToRemove")
    session1.commit()
    
    #deleting the object in session1
    new_object_path = f"{root_object_ownership_relation_attribute}/{'TestPlantToRemove'}"
    
    new_object_id_session1 = session1.get_object(new_object_path).id
    session1.delete_object(new_object_id_session1)
    session1.commit()
    
    #deleting the same object in session2 should fail
    
    with pytest.raises(grpc.RpcError, match="Object not found"):
        new_object_id_session2 = session2.get_object(new_object_path).id
        session2.delete_object(new_object_id_session2)
    
    #commit on session2 is not needed because create should fail
    
    session1.close()
    session2.close()
        
    
@pytest.mark.database
def test_two_sessions_removing_same_object2(connection):
     
    root_object_ownership_relation_attribute = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    #root_object_ownership_relation_attribute_child = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/TestPlantParent.SimpleOwnershipAtt"
        
    session1 = connection.create_session()
    session1.open()
  
    session2 = connection.create_session()
    session2.open()
   
    #first create the object to be deleted
    session1.create_object(root_object_ownership_relation_attribute,"TestPlantToRemove")
    session1.commit()
    
    #deleting the object in session1
    new_object_path = f"{root_object_ownership_relation_attribute}/{'TestPlantToRemove'}"
    
    new_object_id_session1 = session1.get_object(new_object_path).id
    session1.delete_object(new_object_id_session1)
    
    #deleting the same object in session2
    new_object_id_session2 = session2.get_object(new_object_path).id
    session2.delete_object(new_object_id_session2)
    
    #commit on session1 should remove the object
    session1.commit()
    
    #commit on session2 should fail because of object not existing anymore, but it passes - this might be ok, because get_object happens before commit1 so at this point it doesn't verify anymore
    session2.commit()
    
    session1.close()
    session2.close()
    
    
@pytest.mark.database
def test_two_sessions_updating_same_object_same_attribute(connection):
    
    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"
       
    with connection.create_session() as session1:
            
            #get object attributes info with session1
            root_object_full_info_s1 = session1.get_object(root_object_path, full_attribute_info=True)
            string_attribute_s1 = root_object_full_info_s1.attributes["StringAtt"]
            
            #update attribute
            session1.update_simple_attribute(string_attribute_s1, "session1 updated text")
            session1.commit()
            
            #check if attribute has a new value
            assert session1.get_attribute(string_attribute_s1).value == 'session1 updated text'
            
            
    with connection.create_session() as session2:
            
            #get object attributes info with session2
            root_object_full_info_s2 = session2.get_object(root_object_path, full_attribute_info=True)
            string_attribute_s2 = root_object_full_info_s2.attributes["StringAtt"]
            
            #update attribute
            session2.update_simple_attribute(string_attribute_s2, "session2 updated text")
            session2.commit()
            
            #check if attribute has the newest value
            assert session2.get_attribute(string_attribute_s2).value == 'session2 updated text'

    #clean up       
    with connection.create_session() as session3:
            
            #get object attributes info
            root_object_full_info_s3 = session3.get_object(root_object_path, full_attribute_info=True)
            string_attribute_s3 = root_object_full_info_s3.attributes["StringAtt"]
            
            #update attribute to initial value
            session3.update_simple_attribute(string_attribute_s3, "Default string value")
            session3.commit()
     
    
@pytest.mark.database
def test_two_sessions_updating_same_object_different_attributes(connection):
     
    root_object_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1"
            
    with connection.create_session() as session1:
            
            #get object attributes info with session1
            root_object_full_info_s1 = session1.get_object(root_object_path, full_attribute_info=True)
            int_attribute = root_object_full_info_s1.attributes["Int64Att"]
            
            #update attribute
            session1.update_simple_attribute(int_attribute, 100) 
            session1.commit()
            
            #check if attribute has a new value
            assert session1.get_attribute(int_attribute).value == 100
            
            
    with connection.create_session() as session2:
            
            #get object attributes info with session2
            root_object_full_info_s2 = session2.get_object(root_object_path, full_attribute_info=True)
            string_attribute = root_object_full_info_s2.attributes["StringAtt"]
            
            #update attribute
            session2.update_simple_attribute(string_attribute, "updated string")
            session2.commit()
            
            #check if both attributes have new values
            int_attribute_s2 = root_object_full_info_s2.attributes["Int64Att"]
            assert session2.get_attribute(string_attribute).value == 'updated string'
            assert session2.get_attribute(int_attribute_s2).value == 100
   
    #clean up       
    with connection.create_session() as session3:
            
            #get object attributes info
            root_object_full_info_s3 = session3.get_object(root_object_path, full_attribute_info=True)
            string_attribute_s3 = root_object_full_info_s3.attributes["StringAtt"]
            int_attribute_s3 = root_object_full_info_s3.attributes["Int64Att"]

            #update attributes to initial values
            session3.update_simple_attribute(string_attribute_s3, "Default string value")
            session3.update_simple_attribute(int_attribute_s3, 64) 
            session3.commit()
 
@pytest.mark.database
def test_two_sessions_updating_same_object_name(connection):
         
    test_object_ownership_relation_attribute = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    test_object_path0 = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/TestObject"
    test_object_path1 = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/Session1_TestObject_NewName"
    test_object_path2 = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/Session2_TestObject_NewName"


    with connection.create_session() as session1:
        #first create the test object
        session1.create_object(test_object_ownership_relation_attribute,"TestObject")
        session1.commit()
        test_object_id_s0 = session1.get_object(test_object_path0).id
                
        #check if object created with given name
        assert session1.get_object(test_object_id_s0).name == 'TestObject'
        
        #update name in session1
        session1.update_object(test_object_id_s0, new_name="Session1_TestObject_NewName")
        session1.commit()

        test_object_id_s1 = session1.get_object(test_object_path1).id
        assert session1.get_object(test_object_id_s1).name == 'Session1_TestObject_NewName'

    with connection.create_session() as session2:
        
        #update name in session2
        test_object_id_s2 = session2.get_object(test_object_path1).id
        session2.update_object(test_object_id_s2, new_name="Session2_TestObject_NewName")
        session2.commit()
        
        assert session2.get_object(test_object_id_s2).name == 'Session2_TestObject_NewName'
    
    #check that current object name is as committed in session2
    with connection.create_session() as session3:
        test_object_id_s3 = session3.get_object(test_object_path2).id
        assert session3.get_object(test_object_id_s3).name == 'Session2_TestObject_NewName'


    #clean up
    with connection.create_session() as session4:
        new_object_id = session4.get_object(test_object_path2).id
        session4.delete_object(new_object_id)
        session4.commit()

if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))