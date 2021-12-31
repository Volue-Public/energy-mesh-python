Installation
----------------

Python environment
******************

Mesh Python SDK works with Python 3.7.1, 3.8 and 3.9. Support for earlier versions is not provided due to dependencies.

For Python installation help refer to official `Python documentation <https://www.python.org/about/gettingstarted/>`_.


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

    $ my-venv\Scripts\activate.bat (Windows)
    or
    $ source my-venv/bin/activate (Linux, Mac)

#.  :ref:`Install Mesh Python library<Mesh Python library installation>`

Your virtual environment is now up and running with the Mesh Python SDK and you can now develop your project.


Mesh Python library installation
*********************************

Using pip
=========

Recommended way for clients:

::

    python -m pip install git+https://github.com/PowelAS/sme-mesh-python


From source
===========

First clone the repository::

    git clone https://github.com/PowelAS/sme-mesh-python.git


This library uses `Poetry`_ for development, installation, and packaging. To
work with the repository you should `install poetry <https://python-poetry.org/docs/#installation>`_.

To install all our development and runtime dependencies to a virtual environment run::

  poetry install

To create a package run::

  poetry build

It will also (re)generate our grpc/protobuf sources, and should be ran after making changes to those.

To run arbitrary commands in the Poetry environment run::

  poetry run {command}
  # e.g.: poetry run python src\volue\mesh\examples\get_version.py

Or use::

  poetry shell
  # then e.g.: python src\volue\mesh\examples\get_version.py

to drop into a shell with the dependencies available.


Dependencies
*************

The Mesh Python SDK depends on the Python standard library, but also `gRPC <https://grpc.io/>`_ and `Apache Arrow <https://arrow.apache.org/>`_.

These dependencies are managed, installed and referenced by the library using `Poetry`_. So no additional dependencies should be needed after running the pip install, unless you want to run the tests that come with the SDK, then see :ref:`Tests`.

.. _Poetry: https://python-poetry.org/docs/