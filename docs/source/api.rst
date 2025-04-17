API documentation
-----------------

The Mesh Python API contains several packages, namespaces and modules.

volue.mesh
~~~~~~~~~~~~~~~~~~~~

.. We want to include documentation about connection methods, like `with_tls`,
   defined as class methods on Connection base class.
.. automodule:: volue.mesh
    :exclude-members: Connection

    .. autoclass:: Connection
        :inherited-members:
        :exclude-members: WorkerThread


volue.mesh.availability
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: volue.mesh.availability
    :noindex:
    :exclude-members: Availability

    .. autoclass:: Availability
        :inherited-members:
    


volue.mesh.aio
~~~~~~~~~~~~~~~~~~~~

.. automodule:: volue.mesh.aio
    :exclude-members: Connection

    .. autoclass:: Connection
        :inherited-members:
        :exclude-members: WorkerThread


volue.mesh.calc
~~~~~~~~~~~~~~~~~~~~

.. automodule:: volue.mesh.calc
.. automodule:: volue.mesh.calc.common
.. automodule:: volue.mesh.calc.forecast
.. automodule:: volue.mesh.calc.history
.. automodule:: volue.mesh.calc.statistical
.. automodule:: volue.mesh.calc.transform
