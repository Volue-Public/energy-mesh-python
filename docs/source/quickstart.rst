Quickstart guide
-----------------

Here is a quick start guide to setup your first project using the library.

Prerequisites quickstart
**************************

- Supported Python version [3.7.1, 3.8 or 3.9].
- Running Volue Mesh server with gRPC enabled (either locally or on a different machine within your network).

Installation quickstart
**************************

Using pip::

    python -m pip install git+https://github.com/Volue-Public/energy-mesh-python

Recommended way is to use pip with a virtual environment. For more information refer to :doc:`installation`.

First call to Mesh server
**************************

Lets connect to the server, get its version and create a session for getting data.

.. literalinclude:: /../../src/volue/mesh/examples/quickstart.py
   :language: python

Name this file quickstart.py.

.. warning::
   It assumes Volue Mesh server is running locally with gRPC enabled on default port *50051*.
   If you are using a remote server or a non-default port for gRPC communication please change the *address* and *port* variables.
   In case of problems or questions regarding Mesh server configuration please contact Volue consultant.


Now that you made your first script to contact the Volue Mesh server, we have to run the script.::

    $ python quickstart.py

If everything is set up right you should be getting output like the following:

.. highlight:: none

::

    Connected to Volue Mesh Server 99.0.0+0
    You have now an open session and can request timeseries

If there are some problems with this code check out :doc:`faq`.


Next steps
**************************

For more examples refer to :doc:`examples`.