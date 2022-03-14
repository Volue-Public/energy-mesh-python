Mesh Python SDK
---------------------------

The Mesh Python SDK can create a client which is able to communicate with a Mesh server using `gRPC <https://grpc.io/>`_. `Remote procedure calls <https://en.wikipedia.org/wiki/Remote_procedure_call>`_ is a way of sending requests and responses over a network. The request is serialized, using `protocol buffers (aka proto) <https://developers.google.com/protocol-buffers>`_ and packaged then sent to the server which processes the request and sends back a response.

Depending on the request it may take a long time to process by the server. In such cases the client may use package :ref:`api:volue.mesh.aio` which is implemented using the `asyncio <https://docs.python.org/3/library/asyncio.html>`_ library that enables concurrency and lets Python perform other tasks while waiting for the response from the server.

This concept of concurrency can be demonstrated using the following examples. Notice the output of the different examples: 1, 2, A, B vs 1, A, 2, B.

Using :ref:`api:volue.mesh`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_synchronously.py


Using :ref:`api:volue.mesh.aio`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_asynchronously.py

As time series data can potentially be large `Apache Arrow <https://arrow.apache.org/>`_ is used to optimize memory sharing.
