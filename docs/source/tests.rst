Tests
---------

The Mesh Python SDK is shipped with tests that are used to verify its functionality.

.. warning::
   Some tests are written to read or write data to or from the Mesh servers database. These tests are marked with database.

Preparations
*****************

To be able to run the tests there you need `pytest <https://github.com/pytest-dev/pytest>`_ and `pytest-asyncio <https://github.com/pytest-dev/pytest-asyncio>`_. If you followed the instructions in :doc:`installation` all you need to do is: ::

    python -m pip install pytest pytest-asyncio


Run tests
**********************************
Pytest allows you to `specify <https://docs.pytest.org/en/latest/how-to/usage.html#specifying-which-tests-to-run>`_ which tests to run.

Tests can be run from a python script and are grouped to indicate what they do. Available marks are:

.. literalinclude:: ../../pyproject.toml
   :language: toml
   :lines: 37-43
