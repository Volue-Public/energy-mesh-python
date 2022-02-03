Installation
----------------

To be able to communicate with a Mesh server using the Mesh Python SDK some initial setup is needed. Here we suggest one possible setup.

Git
**********

Git is a version control system. To be able to follow along using this guide you will need git to be able to install the Mesh Python SDK.

#. Download and install (Windows):

    * Go to `gitforwindows.org <https://gitforwindows.org/>`_ and download the installer.

    * Installation with default settings should suffice.

#. Configure:

    Git needs to be configured with your name and email address::

        $ git config --global user.name "name"
        $ git config --global user.email "email_address"


GitHub
**********

GitHub is a cloud based storage for git repositories. The Mesh Python SDK is hosted on `GitHub <https://github.com/PowelAS/sme-mesh-python>`_.

To be able to access the code you will need an GitHub user and that user needs to be given access by Volue.

If you don't have a GitHub user you can `join here <https://github.com/join>`_.

Python
**********

Mesh Python SDK works with Python 3.7.1, 3.8 and 3.9. Support for earlier and later versions is not provided due to dependencies.

#. Download and install (Windows):

    #. Go `here <https://www.python.org/downloads/windows/>`_ and download   the latest 3.9 release.

    #. Follow installation instructions. Select "Add Python 3.9 to PATH" for easy access on the command line.

    #. For Python installation help refer to official `Python documentation <https://www.python.org/about/gettingstarted/>`_.

#. Create virtual environment (venv):

    When working with multiple python projects they may depend on different python versions and/or versions of external libraries. For this purpose, the standard library comes with a concept called `Virtual Environments and Packages <https://docs.python.org/3/tutorial/venv.html>`_ to help maintain these separate versions.

    Here is a quick way to set up an virtual environment using the command line:

    #. Create a directory for your project and setup an virtual environment::

        $ mkdir MyProject
        $ cd MyProject
        $ python3 -m venv my-venv

    #. Activate the virtual environment::

        $ my-venv\Scripts\activate.bat (Windows)
        or
        $ source my-venv/bin/activate (Linux, Mac)

    Your virtual environment is now active from the command line.

.. note::
    If you want to use an IDE, like PyCharm, you will need to active the virtual environment for that.


Mesh Python SDK
**********************

Depending on how you intend to use the Mesh Python SDK there are two ways to install it.

If you intend to use it to communicate with a Mesh Server you are a user. If you intend to contribute to development of the SDK you are a developer.

.. _Setup for users:

Setup for users (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a user you can install the Mesh Python SDK using Pythons standard package manager system `pip <https://packaging.python.org/en/latest/tutorials/installing-packages/>`_::

    python -m pip install git+https://github.com/PowelAS/sme-mesh-python

.. note::
    See :doc:`versions` if you need a specific Mesh version.


.. _Setup for developers:

Setup for developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Clone the repository::

    git clone https://github.com/PowelAS/sme-mesh-python.git

#. Install Poetry:

    This library uses `Poetry`_ for development, installation, and packaging. To
    work with the repository you should `install poetry <https://python-poetry.org/docs/#installation>`_.

    To install all our development and runtime dependencies to a virtual environment run::

      poetry install

    To create a package run::

      poetry build

    This will also (re)generate our grpc/protobuf sources, and should be ran after making changes to grpc/proto files.

    To run arbitrary commands in the Poetry environment run::

      poetry run {command}
      # e.g.: poetry run python src\volue\mesh\examples\get_version.py

    Or use::

      poetry shell
      # then e.g.: python src\volue\mesh\examples\get_version.py

    to drop into a shell with the dependencies available.


Dependencies
=============

The Mesh Python SDK depends on the Python standard library, but also `gRPC <https://grpc.io/>`_ and `Apache Arrow <https://arrow.apache.org/>`_.

These dependencies are managed, installed and referenced by the library using `Poetry`_. So no additional dependencies should be needed after running the pip install, unless you want to run the tests that come with the SDK, then see :ref:`tests:Tests`.

.. _Poetry: https://python-poetry.org/docs/


Development environment (IDE)
********************************

To be able to use the Mesh Python SDK to communicate with a Mesh Server or to do development you will need to write Python code that uses the functionality in the Mesh Python package.

There are many ways to do this, but here we present one of them.

.. warning::
    TODO

PyCharm
~~~~~~~~~~~~~~

.. warning::
    TODO
