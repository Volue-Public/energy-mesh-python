Use cases
------------

The use cases are a set of practical tasks set up to show how to get data from a Mesh server connected to a customer database.

Install
******************

Follow the instructions for setting up a new project to work with the Mesh Python SDK in :ref:`installation:Installation`.

Add dependencies
******************

#. Install additional Python packages::

    $ python -m pip install pandas
    $ python -m pip install matplotlib


Get the use cases
*******************

#. Download :download:`use_cases.py <../../src/volue/mesh/use_cases/use_cases.py>`
#. Move the file into your project.

Configure
*************

The use case contains a configuration section, some helper functions and the use cases.

Preferences
~~~~~~~~~~~~~~

The first section of the file exposes some configuration options. Edit these to fit your Mesh server setup and preferences.

.. literalinclude:: /../../src/volue/mesh/use_cases/use_cases.py
   :language: python
   :lines: 17-27

Helper functions
~~~~~~~~~~~~~~~~~~~~

The helper functions gets information about Mesh Python objects, plots or saves timeseries to file.

The use cases
~~~~~~~~~~~~~~

Each use case is tailored to do a specific task on some data from a Mesh server.

All use cases follows this pattern:
First the scenario is explained and needed information is given. Then a connection to the server is established and a new session is created. The information from the scenario is passed into requests that are sent to the server and their response is received. Finally the data is plotted to a figure, saved to file and/or printed to the command line.

An example:

.. literalinclude:: /../../src/volue/mesh/use_cases/use_cases.py
   :pyobject: use_case_1

Edit and run
******************

To be able to test the use case you need to supply information that is in your own Mesh server.
