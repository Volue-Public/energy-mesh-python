Mesh search language
----------------------

The mesh search language can be used to find mesh objects.

To be able to search for a mesh object you need to specify which model to search in, where in the model the search should start and the query matching the criteria of the mesh object you are searching for.

.. note::
    To see what objects the current version of the Mesh Python API supports refer to the api documentation at :ref:`api:volue.mesh` for specific functions that can make use of the search language.


Query syntax
~~~~~~~~~~~~~~

A search consists of a traversal, optionally followed by an :doc:`attribute <mesh_object_attributes>` access (".AttributeName"). A search takes an object (the start point) as input and produces a set of objects or attributes as output (the result). If the attribute access is specified, the result objects are all attributes (attribute search), otherwise they are all objects (object search). The start point is used to form a set and input into the traversal. The attribute access is applied to the output of the traversal. Some of the traversals are parametrized on critera (f.ex. [Critera] or \*[Criteria]).

Traversal
***********

A traversal describes a set of relative paths in the mesh object structure. It takes a set of objects as input (the start points) and produces a set of objects as output (the result) by following the paths from each start point and collecting endpoints. For example, the traversal ‘..’ will output the parent, if it exists, for each input object. Traversals can be combined with operators to form new traversals.

.. image:: images/search1.png

Criteria
*********

Some traversals are parametrized on criteria (see predicated child walk and child step). The criteria controls which objects the traversal will accept as output, and will either accept an object by outputting true or reject it by outputting false. You can combine criteria with operators to form new criteria (see AND, OR). For example, the traversal ‘[.Name=N]’ will for each input object, output the set of child objects whose name equals ‘N’. The traversal ‘\*[.Name=N]’ will for each input object output the set of closest descendant objects whose name is ‘N’.

Criteria are always enclosed in square brackets, [].

You may specify options for the criteria within suffix curly brackets {}, for example to ignore case insensitivity on text based comparison. {i} means the search is case insensitive.


.. image:: images/search2.png


Combining multiple search operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can combine search operations with the following operators:

- **INTERSECTION, &**:
    - The result is the intersection between each result set.
    - Syntax: *Search1&Search2*
- **UNION, \|**:
    - The result is the union between each result set.
    - Syntax: *Search1|Search2*
- **COMPOSITION, /**:
    - Uses the output from Search1 as input to Search2.
    - Syntax: *Search1/Search2*

.. note::
    When using INTERSECTION and UNION between searches, you only use a single character, & or \|, respectively. Inside an object criteria, you use double character to specify a logic AND, &&, or logic OR, \|\|, respectively
