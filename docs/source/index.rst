Welcome to Mesh Python SDK
==============================

Mesh Python SDK is a client library used to
communicate with Volue Energy's Mesh server.

To learn what's new and noteworthy head on over to our :doc:`versions` section.

.. note::
    The Python SDK is currently in `alpha <https://en.wikipedia.org/wiki/Software_release_life_cycle#Alpha>`_

Getting started
----------------

If this is your first time using this library, here are some resources to help you get started.

- **Quickstart:** :doc:`quickstart`
- **Installation:** :doc:`installation`
- **Examples:** :doc:`examples` | :doc:`tests`
- **How to do development** :ref:`Setup for developers`

Features
**************

- Communication using `gRPC <https://grpc.io/>`_
- SDK using ``async``\/``await`` syntax
- Optimised memory sharing by using `Apache Arrow <https://arrow.apache.org/>`_

Prerequisites
**************

- Mesh server with gRPC enabled.
- Python [3.7.1, 3.8, 3.9]

Getting help
---------------

If you're having trouble, these resources might help.

- Try the :doc:`faq` first.
- Report bugs in the `issue tracker <https://github.com/PowelAS/sme-mesh-python/issues>`_

.. toctree::
   :caption: Welcome

   quickstart
   installation
   introduction_to_mesh
   usecases
   examples
   tests
   faq
   glossary

.. toctree::
   :caption: Versions

   versions

.. toctree::
   :caption: SDK Reference

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
