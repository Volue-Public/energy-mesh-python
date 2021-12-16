Tests
---------

The Mesh Python SDK is shipped with tests that are used to verify its functionality.

.. warning::
   Some tests are written to read or write data to or from the Mesh servers database. These tests are marked with database.

Preparations
*****************

To be able to run the tests there you need `pytest <https://github.com/pytest-dev/pytest>`_ and `pytest-asyncio <https://github.com/pytest-dev/pytest-asyncio>`_. If you followed the instructions in :ref:`Introduction` all you need to do is: ::

    python -m pip install pytest pytest-asyncio


Run tests
**********************************
Pytest allows you to `specify <https://docs.pytest.org/en/latest/how-to/usage.html#specifying-which-tests-to-run>`_ which tests to run.

Tests can be run from a python script and are grouped to indicate what they do. Available marks are:

.. literalinclude:: ../../pyproject.toml
   :language: toml
   :lines: 37-43

Tests can be run by doing the following. In case there are failing tests there is the option to generate a report. This will log all except passing tests. More information can be found in `pytests documentation <https://docs.pytest.org/en/latest/how-to/output.html>`_.

.. literalinclude:: ../../src/volue/mesh/examples/run_tests.py
   :language: python


