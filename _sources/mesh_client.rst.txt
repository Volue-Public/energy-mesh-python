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


.. _mesh_client_grpc:

gRPC communication
******************

By default gRPC limits the size of inbound messages to 4MB. From Mesh Python
SDK side, the user can change this limit when creating a connection to Mesh
using `grpc_max_receive_message_length` argument.

See:

* :meth:`volue.mesh.Connection.Session.insecure`
* :meth:`volue.mesh.Connection.Session.with_tls`
* :meth:`volue.mesh.Connection.Session.with_kerberos`
* :meth:`volue.mesh.Connection.Session.with_external_access_token`

Example usage:

.. code-block:: python

    connection = mesh.Connection.with_tls(
        address,
        tls_root_pem_cert,
        grpc_max_receive_message_length=10 * 1024* 1024,  # 10MB
    )


Another example of connection with `grpc_max_receive_message_length` argument
is in `run_simulation.py`.

.. note::
    gRPC outbound message size is not limited by default.

This might be useful when e.g.: running long simulations with
`return_datasets` enabled. In such cases the dataset size might exceed the 4MB
limit and a `RESOURCE_EXHAUSTED` status code would be returned.

However, in other cases like reading time series data, we suggest reading the
data in chunks. E.g.: instead of reading 50 years of hourly time series data
in a single request, the user should request several read operations with
shorter read intervals.

The same is true for writing data, like time series data. Here however, it is
not a suggestion, but a must. Mesh server gRPC inbound message size is not
configurable and therefore it is always equal to 4MB. If gRPC client, like Mesh
Python SDK, sends a message which is too large, then the request will be
discarded. To avoid this, clients must send data in chunks.

.. note::
    Single time series point occupies 20 bytes. To avoid exceeding the 4MB
    limit single read or write operation should contain ~200k points maximum.


Date times and time zones
*************************

The Mesh Python SDK can accept either time zone naive (no time zone information is provided) or time zone aware date time objects.
All time zone naive date time objects are treated as UTC. Time zone aware date time objects are converted to UTC by the Mesh Python SDK before sending to Mesh server.

.. note::
    Time series data returned as PyArrow table is always using UTC to represent timestamps. The user has to convert the timestamps to different format if needed.

.. warning::
    As of PyArrow 7.0.0 the time zone information provided by `dateutil.gettz` is not supported. Please use `datetime.timezone` instead. E.g.:

   .. code-block:: python

      some_tzinfo = timezone(timedelta(hours=-3))

Please refer to the example `timeseries_operations.py` to learn how to work with time zones. Presented below:

.. literalinclude:: /../../src/volue/mesh/examples/timeseries_operations.py
