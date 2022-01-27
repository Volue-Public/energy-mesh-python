News
--------


`Mesh Python SDK version 0.0.2 (alpha) <https://github.com/PowelAS/sme-mesh-python/releases/tag/Mesh_v2.2>`_
*************************************************************************************************************************

------------

New features:
~~~~~~~~~~~~~~~~~~

- Authenticate with Mesh using the Kerberos protocol towards Active Directory.
- Create and/or connect to a session on a running mesh server using both secure and insecure connection.
- Read and write timeseries points using full name, guid or timskey.
- Get and update meta data about timeseries in the resource silo.
- Get and update meta data about timeseries objects connected in the mesh model.
- Search for timeseries objects in the mesh model using the model, a query and either a start path or start guid.
- Rollback and/or commit changes made to a mesh session.
- Documentation, guides and examples.
- Automatic testing.

Changes:
~~~~~~~~~~~~~~~~~~

- First alfa version.

Known issues:
~~~~~~~~~~~~~~~~~~

- **Critical**: "update_timeseries_resource_info(...) is not working as intended" :issue:`116`
- **Major/Minor:** "Writing to a timeseries does not behave as expected" :issue:`115`

Compatible with:
~~~~~~~~~~~~~~~~~~

- Mesh server version 2.2.*
- Python [3.7.1, 3.8 and 3.9]


Install instructions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions in :doc:`installation` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/PowelAS/sme-mesh-python@Mesh_v2.2

