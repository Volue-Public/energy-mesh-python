Quickstart
-----------------

Here is a quick start guide to setup your first project using the library. It assumes you have installed the library and that you have a running Volue Mesh server with gRPC enabled.

Lets connect to the server, get its version, create a session and get some data.

.. literalinclude:: /../../src/volue/mesh/examples/quickstart.py
   :language: python

Name this file quickstart.py.

Now that you made you first script to contact the Volue Mesh server, we have to run the script.::

    $ python quickstart.py

If everything is set up right you should be getting some output. If there are some problems with this code check out :doc:`faq`.