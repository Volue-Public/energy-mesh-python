Concepts
----------------

Basic Concepts
***************

The Mesh Python SDK communicates with a Mesh server using gRPC which is a way of sending requests and responses over a network. The request is serialized and packaged then sent to the server which processes the request and sends back a response.

Depending on the request it may take a long time to process by the server. For such cases the client may use package :ref:`volue.mesh.aio` which is implemented using the asyncio <https://docs.python.org/3/library/asyncio.html>_ library that enables concurrency and lets Python perform other tasks while waiting for the response from the server.

This concept of concurrency can be demonstrated using the following examples.

Using :ref:`volue.mesh`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_synchronously.py


Using :ref:`volue.mesh.aio`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_asynchronously.py


The primary data retrieved from the Mesh server is timeseries. Depending on the request, the size of this data can be quite large. A common scenario is to process this data after it has been acquired and that could mean copying or moving all the data from one library to another. This can be both time consuming and memory intensive, to alleviate these problems the Mesh Python SDK uses `Apache Arrow <https://arrow.apache.org/>`_ to store the data. Several data processing libraries are now supported for this format, including `numpy <https://arrow.apache.org/docs/python/numpy.html>`_ and `pandas <https://arrow.apache.org/docs/python/pandas.html>`_.

Using :ref:`volue.mesh`.Timeseries in a more complete example

.. literalinclude:: /../../src/volue/mesh/examples/timeseries_operations.py
   :language: python