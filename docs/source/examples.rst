Examples
---------

This section contains code examples. Most of them require specific Mesh model on the server side.
Best practice is to copy the examples scripts that are of interest for you together with helpers.py 

Best practices
**************

#. Checkout or open in GitHub git tag corresponding to the Mesh Python SDK
   version you are using. E.g. for Mesh Python SDK v1.7 it is:
   https://github.com/Volue-Public/energy-mesh-python/tree/v1.7.0
#. Copy either the whole `examples` directory or specific examples script(s)
   together with helpers.py and paste it to your own workspace.
#. Run example::

      python .\examples\get_version.py localhost:50051 c:\certificate.pem

   First argument - Mesh server address with port. Default value is
   localhost:50051.

   Second argument - path to PEM-encoded TLS certificate used by Mesh server.
   Skip it if the Mesh server is configured to accept insecure gRPC connections.
   If provided, then make sure that instead of :meth:`volue.mesh.Connection.Session.insecure`,
   the :meth:`volue.mesh.Connection.Session.with_tls` is used to establish
   connection to Mesh.

.. note::
   Starting from Mesh Python SDK 1.9, in all examples the connection to Mesh
   server is established using :meth:`volue.mesh.Connection.Session.insecure`.
   To use a different connection type, e.g.: with TLS, the user has to change
   the example script. The PEM-encoded TLS certificate passed as a second
   argument will be discarded if an insecure connection is used.

Quickstart
*****************
.. literalinclude:: /../../src/volue/mesh/examples/quickstart.py
   :language: python

Authorization
*****************
.. literalinclude:: /../../src/volue/mesh/examples/authorization.py
   :language: python

Connect
*****************
.. literalinclude:: /../../src/volue/mesh/examples/connect_synchronously.py
   :language: python

Connect, asynchronously
*************************
.. literalinclude:: /../../src/volue/mesh/examples/connect_asynchronously.py
   :language: python

Connect using external access token
***********************************
.. literalinclude:: /../../src/volue/mesh/examples/connect_using_external_access_token.py
   :language: python

Get version
************
.. literalinclude:: /../../src/volue/mesh/examples/get_version.py
   :language: python

Read time series
*****************
.. literalinclude:: /../../src/volue/mesh/examples/read_timeseries_points.py
   :language: python

Read time series, asynchronously
********************************
.. literalinclude:: /../../src/volue/mesh/examples/read_timeseries_points_async.py
   :language: python

Read and process time series, asynchronously
********************************************
.. literalinclude:: /../../src/volue/mesh/examples/read_and_process_timeseries_async.py
   :language: python

Search for time series attributes
*********************************
.. literalinclude:: /../../src/volue/mesh/examples/timeseries_search.py
   :language: python

Traverse model
*****************
.. literalinclude:: /../../src/volue/mesh/examples/traverse_model.py
   :language: python

Using time series with pandas
*****************************
.. literalinclude:: /../../src/volue/mesh/examples/timeseries_operations.py
   :language: python

Working with link relations
***************************
.. literalinclude:: /../../src/volue/mesh/examples/working_with_link_relations.py
   :language: python

Working with model (objects and attributes)
*******************************************
.. literalinclude:: /../../src/volue/mesh/examples/working_with_model.py
   :language: python

Working with rating curves
**************************
.. literalinclude:: /../../src/volue/mesh/examples/working_with_rating_curves.py
   :language: python

Working with sessions
*********************
.. literalinclude:: /../../src/volue/mesh/examples/working_with_sessions.py
   :language: python

Working with XY sets
********************
.. literalinclude:: /../../src/volue/mesh/examples/xy_sets.py
   :language: python

Write time series
*****************
.. literalinclude:: /../../src/volue/mesh/examples/write_timeseries_points.py
   :language: python

Run simulations
***************
.. literalinclude:: /../../src/volue/mesh/examples/run_simulation.py
   :language: python

Run inflow calculations
***********************
.. literalinclude:: /../../src/volue/mesh/examples/run_inflow_calculation.py
   :language: python
