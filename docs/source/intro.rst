Introduction
----------------

This is an introduction to the Mesh Python SDK, a gRPC based approach to communicate with Volues Mesh server.

Mesh Python SDK works with Python 3.7 or higher. Support for earlier versions are not provided due to dependencies.

Installing
***********

You can get the library directly from `GitHub <https://github.com/PowelAS/sme-mesh-python>`_

Using pip::

    python -m pip install git+https://github.com/PowelAS/sme-mesh-python


Dependencies
*************

The Mesh Python SDK depends on the Python standard library, but also `gRPC <https://grpc.io/>`_ and `Apache Arrow <https://arrow.apache.org/>`_.

These dependencies are managed, installed and referenced by the library using `Poetry <https://github.com/python-poetry/poetry>`_. So no additional dependencies should be needed after running the pip install, unless you want to run the tests that come with the SDK, then see :ref:`Tests`.

Virtual Environments
********************

When working with multiple python projects they may depend on different python versions or versions of external libraries. For this purpose, the standard library comes with a concept called "Virtual Environments" to help maintain these separate versions.

In-depth information can be found under Pythons official documentation for the `Virtual Environments and Packages <https://docs.python.org/3/tutorial/venv.html>`_.

Here is a quick way:

#. Create a directory for you project::

    $ mkdir MyProject
    $ cd MyProject
    $ python3 -m venv my-venv

#. Activate the virtual environment::

    $ my-env\Scripts\activate.bat (Windows)
    or
    $ source my-venv/bin/activate (Linux, Mac)

#. Use pip to install the Mesh Python library::

    $ python -m pip install git+https://github.com/PowelAS/sme-mesh-python

Your virtual environment is now up and running with the Mesh Python SDK and you can now develop your project.

Basic Concepts
***************

The Mesh Python SDK communicates with a Mesh server using gRPC which is a way of sending requests and responses over a network. The request is serialized and packaged then sent to the server which processes the request and sends back a response.

This process can take some time. The library takes advantage of this if the connection if you are using the package :ref:`volue.mesh.aio` which is implemented using the `asyncio <https://docs.python.org/3/library/asyncio.html>`_ library that enables concurrency and lets Python perform other tasks while waiting for the response from the server.

This concept of concurrency can be demonstrated using the following examples.

Using :ref:volue.mesh`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_synchronously.py


Using :ref:`volue.mesh.aio`.Connection:

.. literalinclude:: /../../src/volue/mesh/examples/connect_asynchronously.py


The primary data retrieved from the Mesh server is timeseries. Depending on the request, the size of this data can be quite large. A common scenario is to process this data after it has been acquired and that could mean copying or moving all the data from one library to another. This can be both time consuming and memory intensive, to alleviate these problems the Mesh Python SDK uses `Apache Arrow <https://arrow.apache.org/>`_ to store the data. Several data processing libraries are now supported for this format, including `numpy <https://arrow.apache.org/docs/python/numpy.html>`_ and `pandas <https://arrow.apache.org/docs/python/pandas.html>`_.

Using :ref:`volue.mesh`.Timeseries with numpy and/or pandas

.. literalinclude:: /../../src/volue/mesh/examples/timeseries_with_numpy_and_pandas.py
   :language: python