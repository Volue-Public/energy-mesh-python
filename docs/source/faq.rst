Frequently Asked Questions
---------------------------

This is a list of frequently asked questions regarding the Mesh Python SDK.

.. contents::
   :local:

When trying to connect to a Volue Mesh server you might get some errors if things are not set up correctly.

I get a connection gRPC error.
******************************
::

    failed to connect to all addresses

This error can have multiple causes. Some things to check are:

#. Is the server **address** correct?
#. Is the server **port** correct?
#. Can you ping the host address?
#. Is the server set up to run with gRPC enabled? For this please contact Volue consultant.


I get a SSL_ERROR_SSL. What am I doing wrong?
*********************************************
::

    E0903 09:26:59.667000000 29912 src/core/tsi/ssl_transport_security.cc:1468] Handshake failed with fatal error SSL_ERROR_SSL: error:100000f7:SSL routines:OPENSSL_internal:WRONG_VERSION_NUMBER.


If your server is set up to not use TLS and you try to connect using a secure connection you will get this error. Either change the server to use TLS (Configuration.Network.GRPC.EnableTLS(true)) or change you client code to connect without a secure connection.


I get an ImportError: cannot import name 'auth_pb2' from 'volue.mesh.proto.auth.v1alpha'.
*****************************************************************************************

When trying to use the Mesh Python SDK you might get an error like this.
All Mesh Python SDK versions up to 1.10.0 (inclusive) are affected by this
issue.

This issue is fixed in Mesh Python SDK 1.11.0. All users with Mesh server
version starting from 2.15.0 should upgrade Mesh Python SDK. Users with Mesh
server version 2.14 and below need to reinstall Mesh Python SDK the following
way:

.. code-block:: bash

   # Generally we recommend to run this in virtual environment
   pip install poetry-core==1.9.1
   pip install grpcio-tools==1.66.1
   # Set your Mesh Python SDK version in the next line
   pip install --no-build-isolation git+https://github.com/Volue-Public/energy-mesh-python@v1.8.0


The reason is that we need poetry-core version below 2.0.0. To do this we need
to install Mesh Python SDK with `--no-build-isolation` flag. This flag requires
all the build dependencies to be already installed on the system. That is why
we install poetry-core and grpcio-tools before installing Mesh Python SDK.

See :issue:`526` for more information.

I get a RESOURCE_EXHAUSTED gRPC error.
**************************************

By default, gRPC limits the size of inbound messages to 4MB. There is no limit
on outbound message size. From client side, the user can change those limits
when creating a gRPC connection to Mesh. From Mesh server side, those limits
are not configurable and the default values are used.

When the server receives too large message, it returns RESOURCE_EXHAUSTED and
a message like "Received message larger than max (20000524 vs. 4194304)".

When the client receives too large message, the client gRPC runtime returns
RESOURCE_EXHAUSTED and a message like "CLIENT: Received message larger than max
(20000524 vs. 4194304)".

Refer to :ref:`Mesh Python SDK gRPC communication <mesh_client_grpc>` for more
information and suggested ways to address the issue.


I get error with building dependencies when installing `volue.mesh` on Linux.
*****************************************************************************

This error can have multiple causes. Some things to check are:

#. Is pip upgraded to the latest version?
#. In particular if there is a problem with building wheel for `kerberos`
   dependency, make sure that `libkrb5-dev`, `python3-dev` and `gcc` are
   installed. For example:

::

  sudo apt-get install libkrb5-dev python3.10-dev gcc

We are automatically verifying that Mesh Python SDK is working for all
supported Python versions using GitHub Actions. Please take a look at the
GitHub Action workflow file to see how are we preparing Windows and Ubuntu
environments:

.. literalinclude:: /../../.github/workflows/usage.yml
   :language: yaml


Other
*****

If neither of the above suggestions helped.

Mesh server gRPC configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mesh server is configured by Volue consultants. In case of any configuration problems or change requests (like turning on authentication) please contact your Volue consultant.


I think I found a bug or I have a feature request.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you believe you found a bug in the Mesh Python SDK or have any other suggestions, you should first read the `discussion board <https://github.com/Volue-Public/energy-mesh-python/discussions>`_ and if that does not resolve your problem you should report the issue in as much detail as possible, preferably with a code example demonstrating the bug, in `issue tracker <https://github.com/Volue-Public/energy-mesh-python/issues>`_.


I need more help.
~~~~~~~~~~~~~~~~~~~~~~

If you have a more pressing issue or if your issue includes confidential information, you should contact Volue's customer service.
