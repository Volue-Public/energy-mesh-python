Attributes
---------------

Mesh object can have **attributes** (aka properties) connected to them. An attribute consists for a **definition** and possibly a **value** of some type. All mesh object has *Type* and *Name* as implicit attributes and then optionally any number of extra attributes.

Here are a few non-exhaustive examples of attributes:

A **time series attribute** is defined to have a name and a unit of measurement. The value is a reference to a physical time series entry which is store in the underlying database.

A **time series calculation attribute** is defined to have a name, a unit of measurement and a default template expression. If the default template expression is to be overridden a field is added with a local expression. **Expressions** are valid combinations of :doc:`functions <mesh_functions>` calls.

A **double attribute** is defined to have a name, a default value of the type Double. If the double attribute is set to have its value set to something other than the default value the attribute will have an additional field of type Double with the specific value set.