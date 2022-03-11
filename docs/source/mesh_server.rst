Mesh server
---------------------------

The Volue Mesh server is an application built to handle incoming requests from clients. One way of handling such requests is by `remote procedure calls <https://en.wikipedia.org/wiki/Remote_procedure_call>`_. The Mesh Python API is able to connect to the Mesh server using `gRPC <https://grpc.io/>`_. The server has to be configured to listen for this kind of communication. To be able to connect you need the Mesh server's IP address and the port open for RPC calls.

Communication with the server can either be insecure or secured by encryption. The Mesh server supports `TLS (transport layer security) <https://en.wikipedia.org/wiki/Transport_Layer_Security>`_ which is a protocol designed to provide communication's security over a computer network through the use of certificates.

Access to the server can be further secured by requiring users to :doc:`authenticate <authentication>` with an `active directory (AD) <https://en.wikipedia.org/wiki/Active_Directory>`_ service. The user will then be authorized to access data based on the permissions set in AD. Authorized user will get an access token from Mesh server. This requires that communication with the server is secured using encryption as explained above.

When connected, authenticated and authorized the user will be able to create a :doc:`mesh_session` within the Mesh server. A session is a temporal workspace and should be created and closed.

.. toctree::
   :hidden:

   authentication
   mesh_session