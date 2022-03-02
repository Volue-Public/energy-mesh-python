:orphan:
.. TODO Work in progress

Mesh client
---------------------------




.. Comment
    - mesh client, python api, technical (.rts)
        - gRPC, proto
        - Python api
            - versions
        - sync vs async
        - secure vs unsecure connection, tls
        - apache arrow


Connection
***************

The Mesh Python SDK communicates with a Mesh server using gRPC which is a way of sending requests and responses over a network. The request is serialized and packaged then sent to the server which processes the request and sends back a response.

Depending on the request it may take a long time to process by the server. For such cases the client may use package :ref:`api:volue.mesh.aio` which is implemented using the `asyncio <https://docs.python.org/3/library/asyncio.html>`_ library that enables concurrency and lets Python perform other tasks while waiting for the response from the server.

This concept of concurrency can be demonstrated using the following examples.

Using :ref:`api:volue.mesh`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_synchronously.py


Using :ref:`api:volue.mesh.aio`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_asynchronously.py