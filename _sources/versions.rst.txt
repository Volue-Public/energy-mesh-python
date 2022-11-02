Versions
--------

Depending on the Mesh Server version you intend to communicate with a compatible version of Mesh Python SDK is needed.

`Mesh Python SDK version 1.0.0 (Release Candidate) <https://github.com/Volue-Public/energy-mesh-python/releases/tag/v1.0.0>`_
*****************************************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version >= 2.6.1
- Python [3.7.1, 3.8 and 3.9]
- Tested with Mesh server version 2.6.1.8

New features
~~~~~~~~~~~~~~~~~~

- Implement XY sets. :issue:`230`
- Implement link relations. :issue:`229`
- Implement RatingCurve attribute. :issue:`228`

Changes
~~~~~~~~~~~~~~~~~~

- **Enhancement:** Add example with traversing a model using the relation attributes. :issue:`309`
- **Enhancement:** Support for instances of *Object* and *AttributeBase* as *target* for session methods. :issue:`267`
- **Enhancement:** Unify arguments of all session methods. :issue:`266`
- **Enhancement:** Ownership relation attribute improvements. PR :pull:`296`
- **Enhancement:** Improve examples for reading and writing time series. PR :pull:`293`
- **Enhancement:** Extend time series point flags. PR :pull:`272`
- **Fixed:** Attributes with empty values are instantiated as *AttributeBase*. :issue:`306`
- **Fixed:** Fix argument typing hints in *calc* module. PR :pull:`286`
- **Fixed:** Fix async *search_for_objects*. PR :pull:`281`

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@v1.0.0


`Mesh Python SDK version 0.0.4 (alpha) <https://github.com/Volue-Public/energy-mesh-python/releases/tag/Mesh_v2.5>`_
*************************************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version 2.5.*
- Python [3.7.1, 3.8 and 3.9]
- Tested with Mesh server version 2.5.0.14

New features
~~~~~~~~~~~~~~~~~~

- Sum function for single time series. :issue:`161`
- Read of virtual timeseries in SmG. :issue:`153`
- Logging and audit trail. :issue:`156`
- Read and write of objects in the physical Mesh model. :issue:`151`
- Implement RPCs for handling attributes. :issue:`203`

Changes
~~~~~~~~~~~~~~~~~~

- **Enhancement:** Separate forecasting and history functions. :issue:`113`
- **Enhancement:** Readable error for reply with no timeseries data. :issue:`164`
- **Enhancement:** Expose transformation functions the same way other calc functions are exposed. :issue:`157`
- **Fixed:** Dependencies not set correctly :issue:`178`
- **Fixed:** Inconsistent handling of timestamps in time series data point update. :issue:`183`

Known issues
~~~~~~~~~~~~~~~~~~

- Lacking support to read and write XYZ attributes and link relations.

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@Mesh_v2.5


`Mesh Python SDK version 0.0.3 (alpha) <https://github.com/Volue-Public/energy-mesh-python/releases/tag/Mesh_v2.3>`_
*************************************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version 2.3.*
- Python [3.7.1, 3.8 and 3.9]
- Tested with Mesh server version 2.3.0.12

New features
~~~~~~~~~~~~~~~~~~

- Read transformed timeseries. :issue:`100`
- Read historical timeseries. :issue:`101`, :issue:`102`

Changes
~~~~~~~~~~~~~~~~~~

- **Enhancement:** Adding more usecases. :issue:`109`
- **Enhancement:** Proto files reorganized. :issue:`133`
- **Enhancement:** Various documentation updates. :issue:`138`, :issue:`134`
- **Enhancement:** "Expose TLS credential settings" :issue:`135`
- **Fixed:** "read_timeseries_points(...) returns either a List[Timeseries] or just Timeseries" :issue:`125`
- **Fixed:** "update_timeseries_resource_info(...) is not working as intended" :issue:`116`
- **Fixed:** "Writing to a timeseries does not behave as expected" :issue:`115`
- **Fixed:** "get_timeseries_attribute(...) won't accept GUIDs from Nimbus" :issue:`120`
- **Fixed:** "Visual bug when displaying results for use cases" :issue:`122`

Known issues
~~~~~~~~~~~~~~~~~~

- None

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@Mesh_v2.3



`Mesh Python SDK version 0.0.2 (alpha) <https://github.com/Volue-Public/energy-mesh-python/releases/tag/Mesh_v2.2>`_
*************************************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version 2.2.*
- Python [3.7.1, 3.8 and 3.9]
- Tested with Mesh server version 2.2.0.9

New features
~~~~~~~~~~~~~~~~~~

- Authenticate with Mesh using the Kerberos protocol towards Active Directory.
- Create and/or connect to a session on a running Mesh server using both secure and insecure connection.
- Read and write timeseries points using full name, GUID or timskey.
- Get and update metadata about physical Oracle timeseries.
- Get and update metadata about timeseries objects connected in the Mesh model.
- Search for timeseries objects in the Mesh model using the model, a query and either a start path or start guid.
- Rollback and/or commit changes made to a Mesh session.
- Documentation, guides and examples.
- Automatic testing.

Changes
~~~~~~~~~~~~~~~~~~

- First alpha version.

Known issues
~~~~~~~~~~~~~~~~~~

- **Critical**: "update_timeseries_resource_info(...) is not working as intended" :issue:`116`
- **Major/Minor:** "Writing to a timeseries does not behave as expected" :issue:`115`
- **Major:** "get_timeseries_attribute(...) won't accept GUIDs from Nimbus" :issue:`120`
- **Minor:** "Visual bug when displaying results for use cases" :issue:`122`

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@Mesh_v2.2

