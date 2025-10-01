========
Sessions
========

Please refer to `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/sessions/>`_
for a general description of session concept in Mesh.

The following example shows some different ways of working with sessions.

.. literalinclude:: /../../src/volue/mesh/examples/working_with_sessions.py


Timeout
~~~~~~~

To make working with Mesh via Python SDK more user-friendly the extension of
session lifetime is handled automatically by the Mesh Python SDK. So as long
as you have an opened session, the Python SDK will send automatically calls to
extend the session lifetime in the background.

In very limited and special use case where you want to connect to already
existing and opened session via :ref:`api:volue.mesh`.Connection.connect_to_session
Python SDK will not automatically extend the lifetime of the session. In such
case the user needs to make explicit calls. This is because tracking of an open
session that needs automatic lifetime extension is started when it is open via
Python's :ref:`api:volue.mesh`.Connection.Session object.
