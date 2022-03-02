Mesh functions
---------------

An **expressions** can be used to access **functions** available in Mesh. The result of a calculation based on a function is a temporary time series, i.e. a series which is not in the database. Every time the calculation expression is run, values are calculated for the temporary time series, which can then be displayed in a table. However, the result is only available when the Mesh session is open.

The Mesh :doc:`search language <mesh_search>` can be used inside functions to find specific objects to work on.

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

- Fixed interval time series, break point series
- Single value
- array of time series

Statistical
~~~~~~~~~~~~~~

.. automodule:: volue.mesh.calc.statistical.StatisticalFunctions
   :members:
   :noindex:

Transformation
~~~~~~~~~~~~~~~

.. automodule:: volue.mesh.calc.transform
   :noindex:

History
~~~~~~~~~~~~~~

.. autoclass:: volue.mesh.calc.history.HistoryFunctions
   :members:
   :noindex:
