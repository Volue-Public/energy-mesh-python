Mesh functions
---------------

**Expressions** can be used to access **functions** available in Mesh. The result of a calculation based on a function is a temporary time series, i.e. a time series which is not in the database. Every time the calculation expression is run, values are calculated for the temporary time series. However, the result is only available when the Mesh session is open.

The Mesh :doc:`search language <mesh_search>` can be used with functions to find specific objects to work on.

Definition of a Mesh function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions are identified with a name and an unprotected identifier, and are distinguished from variables by the first character: an @-symbol. The same function name can have several argument combinations.

The function's argument is placed in parenthesis ( ). A function can have any number of arguments, including 0.

Example showing expressions made using functions:

- Expression A equals a number
    - A = 5
- Expression B equals the result of the sum of two MAX functions using expression A and the max value in time series EnTS
    - B = @MAX(A, 55) + @MAX(%EnTS)

Valid result types from functions:

- Single time series
- Array of time series
- Single double value
- Array of double values
- Single string value
- Array of string values


.. note::
   Mesh Python SDK is providing wrappers for the calculation functions. See next sections.

Forecast
~~~~~~~~~~~~~~

.. automodule:: volue.mesh.calc.forecast
   :noindex:

History
~~~~~~~~~~~~~~

.. automodule:: volue.mesh.calc.history
   :noindex:

Statistical
~~~~~~~~~~~~~~

.. automodule:: volue.mesh.calc.statistical
   :noindex:

Transformation
~~~~~~~~~~~~~~~

.. automodule:: volue.mesh.calc.transform
   :noindex:
