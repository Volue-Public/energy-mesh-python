========
Sessions
========

Please refer to `Mesh documentation <https://docs.volue.com/optimisation-and-planning/smart-power/mesh/concepts/sessions/>`_
for a general description of session concept in Mesh.

The following example shows some different ways of working with sessions.

.. literalinclude:: /../../src/volue/mesh/examples/working_with_sessions.py


Timeout
~~~~~~~

To make working with Mesh via Python SDK more user-friendly the extension of
session lifetime is handled automatically by the Mesh Python SDK. So as long
as you have an opened session, the Python SDK will automatically send calls to
extend the session lifetime in the background.

In the very limited and special use case where you want to connect to an
already existing and opened session via
:py:meth:`volue.mesh.Connection.connect_to_session` Python SDK will not
automatically extend the lifetime of the session. In such case the user needs
to make explicit calls. This is because tracking of an open session that needs
automatic lifetime extension is started when it is opened via Python's
:py:class:`volue.mesh.Connection.Session` object.


Good practices
~~~~~~~~~~~~~~

* Close unused sessions. If you create the session with a ``with`` statement,
  it is closed automatically when the block exits, even if an exception is
  raised. Otherwise you should close it explicitly using
  :py:meth:`volue.mesh.Connection.Session.close`. Every open session occupies
  resources on the Mesh server and runs a background thread in the Python SDK
  that extends its lifetime, see `Timeout`_ above.

* If possible, reuse the same session for multiple calls to the server,
  instead of creating a new session for each call. Opening and closing a
  session requires additional calls to the Mesh server and starting a new
  lifetime extension thread, so reusing a session reduces this overhead.

* Commit changes before closing a session. Closing a session discards all
  uncommitted changes, so call :py:meth:`volue.mesh.Connection.Session.commit`
  for the changes you want to keep. No explicit rollback is needed for changes
  you want to discard.
