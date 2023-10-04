Versions
--------

Depending on the Mesh Server version you intend to communicate with a compatible version of Mesh Python SDK is needed.

`Mesh Python SDK version 1.4.0 <https://github.com/Volue-Public/energy-mesh-python/releases/tag/v1.4.0>`_
*********************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version >= 2.10
- Python [3.8 3.9, 3.10 and 3.11]

New features
~~~~~~~~~~~~~~~~~~

- Implement automatic session lifetime extension :pull:`368`
- Implement functionality to get model names :issue:`356`

Changes
~~~~~~~~~~~~~~~~~~

- **Fixed:** Handling simple attributes without any values. :pull:`364`
- Versions must be sorted in update_rating_curve_versions :pull:`358`


Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@v1.4.0

.. warning::
    For Python 3.11 on Windows do not use Git BASH for installing Mesh Python
    SDK. You may get an error when building `wheel` for `winkerberos` which is
    one of Mesh Python SDK dependencies.

    For Python 3.11 on Windows make sure you have Microsoft Visual C++ 14.0 or greater installed.
    Get it with `Microsoft C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_.


`Mesh Python SDK version 1.3.0 <https://github.com/Volue-Public/energy-mesh-python/releases/tag/v1.3.0>`_
*********************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version >= 2.9
- Python [3.8 3.9, 3.10 and 3.11]

New features
~~~~~~~~~~~~~~~~~~

- Support for Python 3.11 :pull:`359`

.. warning::
    Python 3.7.1 is no longer supported.

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@v1.3.0

.. warning::
    For Python 3.11 on Windows do not use Git BASH for installing Mesh Python
    SDK. You may get an error when building `wheel` for `winkerberos` which is
    one of Mesh Python SDK dependencies.

    For Python 3.11 on Windows make sure you have Microsoft Visual C++ 14.0 or greater installed.
    Get it with `Microsoft C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_.


`Mesh Python SDK version 1.2.1 <https://github.com/Volue-Public/energy-mesh-python/releases/tag/v1.2.1>`_
*********************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version >= 2.9
- Python [3.7.1, 3.8 3.9 and 3.10]

New features
~~~~~~~~~~~~~~~~~~

- Connection using external access token (e.g.: OAuth JWT access token) (:pull:`347` and :pull:`349`)

Changes
~~~~~~~~~~~~~~~~~~

- **Fixed:** Parsing root objects. :pull:`354`

.. warning::
    Python 3.7.1 support will dropped in the next Mesh Python SDK release.

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@v1.2.1


`Mesh Python SDK version 1.1.1 <https://github.com/Volue-Public/energy-mesh-python/releases/tag/v1.1.1>`_
*********************************************************************************************************

------------

Compatible with
~~~~~~~~~~~~~~~~~~

- Mesh server version >= 2.6.1
- Python [3.7.1, 3.8 3.9 and 3.10]
- Tested with Mesh server version 2.6.1.8

New features
~~~~~~~~~~~~~~~~~~

- Support for Python 3.10 :pull:`93`

Changes
~~~~~~~~~~~~~~~~~~

- **Fixed:** Reading empty time series attributes :issue:`346`

Install instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See instructions at :ref:`Setup for users` and use the following:

::

    python -m pip install --force-reinstall git+https://github.com/Volue-Public/energy-mesh-python@v1.1.1


`Mesh Python SDK version 1.0.0 <https://github.com/Volue-Public/energy-mesh-python/releases/tag/v1.0.0>`_
*********************************************************************************************************

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

