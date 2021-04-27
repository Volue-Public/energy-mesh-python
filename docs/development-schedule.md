# Mesh Python Development Schedule

This document contains the up-to-date plans for developing the Mesh Python SDK.

NB! Any description in this document describes how we plan to do things, but no commitments to what the final product will be. All content may change if better solutions are identified.

## Functions to implement

The list below is in the prioritized order of completing the different functions. 

NB! Function names are so far only to signal functionality, and they will change during implementation.

1. Functions to connect to a Mesh session
   * open-connection with user
   * start-transaction
   * commit-transaction
   * rollback-transaction
   * close-connection

2. Functions to read and write time series data
   * read-timeseries-data identified by guid
     * for single time series
     * for multiple time series
   * write-timeseries-data identified by guid
     * for single time series
     * for multiple time series

3. Functions to search for time series in a Mesh model
   * search-timeseries-attr using model path search
     * may return a number of time series attributes/references
   * search-timeseries-refs using time series references
     * using filename+tscode or tims-key
     * may return a number of time series references

4. Functions to access structural and time series objects in a Mesh model
   * search-object using model path search
     * may return a number of object guids
   * get-object reads an object using guid
   * ...

5. Functions to create, update and delete objects in a Mesh model. 
   * create-object creates an object with attributes
   * update-object updates attributes on an object
   * delete-object deletes an object

## Sprint content

* **Sprint 1** - week 14-16
  
  Set up all build dependencies necessary to support Python development. A simple test function to allow read of time series data out of Mesh is implemented.

* **Sprint 2** - week 17-19
  
  Start implementing security related to the new APIs. All communication shall be encrypted using HTTPs. We will try to implement integration with an authentication provider using standard Kerberos correctly. Kerberos is selected because that is still what is in use in the other SmE applications, but this may very well be changed in a later stage based on general Volue recommendations.

  Authorisation requirements for the first Python version is to limit access to None/Read/Write either time series data and objects.

  In addition will implementation be started on functions related to read and write time series data.

  By the end of the sprint, the sme-mesh-python repository will be made externally available for the Flow partners.

* **Sprint 3** - week 20-22

  Start implementing internal Mesh functionality related to logging of requests received over gRPC and Python. Logging will be based on a common datastore - currently the existing Powel Event Log. Events logged could be for instance:
  * Write activities such that there is an overview of who writes what when. Further information such as successful writes and failed writes.
  * Read activities such that there is an overview of who reads what when.
  * Activities not authorized to the user.
  
  In addition, we will start to log all changes transferred over gRPC and Python to the common audit log of Mesh.

* **Further sprints** - every 3 weeks. Content to be defined when we see the progress of the three first sprints.
