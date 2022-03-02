Versions
--------

Depending on the Mesh Server version you intend to communicate with a compatible version of Mesh Python SDK is needed.


`Mesh Python SDK version 0.0.3 (alpha) <https://github.com/PowelAS/sme-mesh-python/releases/tag/Mesh_v2.3>`_
*************************************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version 2.3.*
- Python [3.7.1, 3.8 and 3.9]

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

- **Minor**: "History functions might return time series data in a different timezone than UTC" :issue:`146`

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/PowelAS/sme-mesh-python@Mesh_v2.3



`Mesh Python SDK version 0.0.2 (alpha) <https://github.com/PowelAS/sme-mesh-python/releases/tag/Mesh_v2.2>`_
*************************************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version 2.2.*
- Python [3.7.1, 3.8 and 3.9]

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

    python -m pip install --force-reinstall git+https://github.com/PowelAS/sme-mesh-python@Mesh_v2.2

