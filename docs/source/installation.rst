Installation
----------------

To be able to communicate with a Mesh server using the Mesh Python SDK some initial setup is needed. Here we suggest one possible setup.

Git
**********

Git is a version control system. To be able to follow along using this guide you will need git to be able to install the Mesh Python SDK.

#. Download and install:

    * Go to `git-scm.com <https://git-scm.com/downloads>`_ and download the installer.

    * Installation with default settings should suffice.

#. Configure:

    Git needs to be configured with your name and email address::

        $ git config --global user.name "name"
        $ git config --global user.email "email_address"


GitHub
**********

GitHub is a cloud based storage for git repositories. The Mesh Python SDK is hosted on `GitHub <https://github.com/Volue-Public/energy-mesh-python>`_.

To be able to access the code you will need a GitHub user and that user needs to be given access by Volue.

If you don't have a GitHub user you can `join here <https://github.com/join>`_.


Python
**********

Mesh Python SDK works with Python 3.9, 3.10, 3.11, 3.12 and 3.13. Support for earlier and later versions is not guaranteed due to dependencies.

#. Download and install (Windows):

    #. Go to `python.org <https://www.python.org/downloads/windows/>`_ and download the latest supported release.

    #. Follow installation instructions. Select "Add Python 3.xx to PATH" for easy access on the command line.

    #. For Python installation help refer to official `Python documentation <https://www.python.org/about/gettingstarted/>`_.


Development environment
***************************

To be able to use the Mesh Python SDK to communicate with a Mesh Server or to do development you will need to write Python code that uses the functionality in the Mesh Python package.

There are many ways to do this, but here we present one of them.

PyCharm
~~~~~~~~~~~~~~

PyCharm is an IDE designed to write and execute Python code.

When working with multiple python projects they may depend on different python versions and/or versions of external libraries. For this purpose, the standard library comes with a concept called `Virtual Environments and Packages <https://docs.python.org/3/tutorial/venv.html>`_ to help maintain these separate versions.

#. Download and install:

    a. Go `here <https://www.jetbrains.com/pycharm/download/#section=windows>`_ and download the installer.

    #. Run the installer and follow the steps in the installation wizard.

#. Create a `new project <https://www.jetbrains.com/help/pycharm/creating-and-running-your-first-python-project.html#creating-simple-project>`_.

#. Create a `python file <https://www.jetbrains.com/help/pycharm/creating-and-running-your-first-python-project.html#create-file>`_ for your code.

#. Good to know:

    a. PyCharm Terminal:

        'View' -> 'Tool Windows' -> 'Terminal' will bring up a command line where the virtual environment is activated.

        .. note::
            This is the command line where you should run commands for installing new packages. Example: 'python -m pip install <some_python_package>'.

    #. Execute a script:

        Right click on the <your_python_script>.py in the 'Project' view to the right in PyCharm and select 'Run'.


Mesh Python SDK
**********************

Depending on how you intend to use the Mesh Python SDK there are two ways to install it.

If you intend to use it to communicate with a Mesh Server you are a user. If you intend to contribute to development of the SDK you are a developer.

.. _Setup for users:

Setup for users (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a user you can install the Mesh Python SDK using Python's standard package manager system `pip <https://packaging.python.org/en/latest/tutorials/installing-packages/>`_::

    python -m pip install git+https://github.com/Volue-Public/energy-mesh-python

.. note::
    See :doc:`versions` if you need a specific Mesh version.


Setup for users (offline environments)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install Mesh Python SDK on a computer without internet connection you first need to download
binaries on a computer with internet connection and then copy those binaries to the target machine.

On computer with internet connection download the Mesh Python SDK along with its dependencies using
Python's standard package manager system pip::

    # Use correct volue.mesh package version.
    python -m pip download git+https://github.com/Volue-Public/energy-mesh-python@vX.Y.Z


Additionally, download Mesh Python SDK build dependencies. Those are specified in the [build-system]
section in pyproject.toml file.::

    # Check [build-system] section in pyproject.toml file if those are up to date.
    python -m pip download poetry-core==1.9.1
    python -m pip download grpcio-tools==1.67.1

Copy all the downloaded binaries to the target computer without internet connection.
In the directory with the downloaded binaries execute::

    # Use correct volue.mesh package version.
    python -m pip install volue.mesh-X.Y.Z.zip --no-index -f .

.. note::
    See :doc:`versions` if you need a specific Mesh version.

.. _Setup for developers:

Setup for developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Clone the repository::

    git clone https://github.com/Volue-Public/energy-mesh-python.git

#. Install Poetry:

    This library uses `Poetry`_ for development, installation and packaging. To
    work with the repository you should `install poetry <https://github.com/python-poetry/poetry#installation>`_.
    The steps below assume Poetry binary is added to your PATH.

    To install all our development and runtime dependencies to a virtual environment go to the Mesh Python SDK repository directory and run::

      poetry install

    To create a package run::

      poetry build

    This will also (re)generate our grpc/protobuf sources, and should be ran after making changes to proto file(s).

    To run arbitrary commands in the Poetry environment run::

      poetry run {command}
      # e.g.: poetry run python src\volue\mesh\examples\get_version.py

    Or use::

      poetry shell
      # then e.g.: python src\volue\mesh\examples\get_version.py

    to drop into a shell with the dependencies available.

#.  For the development we are using `Black <https://github.com/psf/black>`_
    auto formatter. It is added as a development dependency and installed
    automatically by Poetry, so you don't need to install anything extra.
    Before committing your changes and creating a Pull Request to Python SDK
    repository make sure the code is correctly formatted, by running::

        poetry run black .

    Most IDEs have options to automate the usage of auto formatters like
    *Black*, e.g.: the formatting can be executed on file save, so you don't
    need to make an explicit call like presented above.

Tests
=====

There are different types of tests. Some tests require running Mesh server
instance with specific test model named: SimpleThermalTestModel. Such tests are
marked with `database`. Other types like `unittest` do not require Mesh server
at all. To see all types of tests see `markers` in [tool.pytest.ini_options]
section in pyproject.toml file.

Pytest allows you to `specify <https://docs.pytest.org/en/latest/how-to/usage.html#specifying-which-tests-to-run>`_
which tests to run. For example, to check all tests except authentication and
long tests::

    poetry run pytest -m "not authentication and not long"


When submitting a new Pull Request the tests are run automatically using GitHub
Actions.


Dependencies
=============

The Mesh Python SDK depends on the Python standard library, but also `gRPC <https://grpc.io/>`_ and `Apache Arrow <https://arrow.apache.org/>`_.

These dependencies are managed, installed and referenced by the library using `Poetry`_.
No additional dependencies should be needed after running the pip install.

.. _Poetry: https://python-poetry.org/docs/

Version compatibility
=====================

The Mesh Python SDK will perform the version compatibility check when connecting to the Mesh server.
It will ask the server for its version number and will validate it according to the rules
found in the :doc:`versions` section.

The Mesh server will also perform the version compatibility check based on the version
sent by the Mesh Python SDK in the gRPC request metadata.
For the version metadata to be correctly populated, the `volue.mesh` package
should be installed using the :ref:`recommended procedure <Setup for users>`.
When using the Mesh Python SDK directly from the source,
the version compatibility check will be skipped.
