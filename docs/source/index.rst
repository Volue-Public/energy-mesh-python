Welcome to Mesh Python SDK
==============================

Mesh Python SDK that can be used to
communicate with Volue Energy's Mesh server.

Getting started
----------------

If this is you first time using this library, here are some resources to help you get started.

- **First steps:** :doc:`intro` | :doc:`quickstart`
- **Examples:** See the `repository <https://github.com/PowelAS/sme-mesh-python/tree/master/examples/mesh>`_

Features
**************

- Communication using `gRPC <https://grpc.io/>`_
- SDK using ``async``\/``await`` syntax
- Optimised memory sharing by using `Apache Arrow <https://arrow.apache.org/>`_

Prerequisites
**************
(<TODO> - autoextract version info from config file)
- Mesh server with gRPC enabled. > ???
- Python > 3.7

Getting help
---------------

If you're having trouble, these resouces might help.

- Try the :doc:`faq` first.
- Report bugs in the `issue tracker <https://github.com/PowelAS/sme-mesh-python/issues>`_

.. toctree::
   :caption: Welcome

   intro
   quickstart
   examples
   faq
   glossary

.. toctree::
   :caption: SDK Reference

   credentials
   connection
   async_connection
   common
   timeserie


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
