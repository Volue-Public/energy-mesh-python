Frequently Asked Questions
---------------------------

This is a list of frequently asked questions regarding the Mesh Python SDK.

.. contents::
   :local:

Connection errors
******************

When trying to connect to a Volue Mesh server you might get some errors if things are not set up correctly.

I get a gRPC error.
~~~~~~~~~~~~~~~~~~~~
::

    failed to connect to all addresses

This error can have multiple causes. Some things to check are:

#. Is the server **address** correct?
#. Is the server **port** correct?
#. Can you ping the host address?
#. Is the server set up to run with gRPC enabled? For this please contact Volue consultant.


I get a SSL_ERROR_SSL. What am I doing wrong?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    E0903 09:26:59.667000000 29912 src/core/tsi/ssl_transport_security.cc:1468] Handshake failed with fatal error SSL_ERROR_SSL: error:100000f7:SSL routines:OPENSSL_internal:WRONG_VERSION_NUMBER.


If your server is set up to not use TLS and you try to connect using a secure connection you will get this error. Either change the server to use TLS (Configuration.Network.GRPC.EnableTLS(true)) or change you client code to connect without a secure connection.


Other
*****

If neither of the above suggestions helped.

I ran the tests and one or more of them failed.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you ran the :ref:`tests:Tests` and one or more of them failed, you should first verify that you configured the server connection correctly. If the problem is not resolved by this you can generate a report based on the tests you ran by following the instructions in :ref:`tests:Run tests`.


Mesh server gRPC configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mesh server is configured by Volue consultants. In case of any configuration problems or change requests (like turning on authentication) please contact your Volue consultant.


I think I found a bug or I have a feature request.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you believe you found a bug in the Mesh Python SDK or have any other suggestions, you should first read the `discussion board <https://github.com/PowelAS/sme-mesh-python/discussions>`_ and if that does not resolve your problem you should report the issue in as much detail as possible, preferably with a code example demonstrating the bug, in `issue tracker <https://github.com/PowelAS/sme-mesh-python/issues>`_.


I need more help.
~~~~~~~~~~~~~~~~~~~~~~

If you have a more pressing issue or if your issue includes confidential information, you should contact Volue's customer service.

