======================
External authorization
======================

Mesh server could be protected by external authorization server, where the
clients like Python SDK authenticate and request access tokens. Tokens obtained
from external authorization servers are then send in the `Authorization` header
when making a call to the Mesh API.

This is required by the Mesh server if *OAuth* is enabled for the gRPC
interface in the Mesh configuration file.

For security reasons authentication also requires TLS to be enabled, and
you might therefore need Mesh's TLS certificate in the below examples.


Token format
****************

Mesh supports OAuth 2.0 JSON Web Token (JWT) access tokens. They need to meet
the following requirements:

- Access token signed using RSA algorithm.
- Authorization is done using `roles` claim that must be part of the access
  token.
- User's claims: `name` and `oid` must be part of the access token.

Azure Active Directory (Azure AD) supports all OAuth 2.0 flows.


Example
*******

.. code-block:: python

	from volue import mesh

	# Most certificates won't work with IP addresses, therefore
	# you'll need to be able to resolve the Mesh server by name,
	# either through your DNS configuration, or through /etc/hosts.
	with open("certificate.pem", "rb") as f:
	    certificate = f.read()

	token = "my_access_token"  # obtain it from authorization server

	# mesh.domain.com is the address of the Mesh server.
	connection = mesh.Connection.with_external_access_token(
	    "mesh.domain.com:50051", certificate, token
	)
	print(connection.get_user_identity())


For more complex example please refer to *connect_using_external_access_token.py*:

.. literalinclude:: /../../src/volue/mesh/examples/connect_using_external_access_token.py


Internals
*********

Mesh validates **access tokens** that are send with every call to the server.
Validation means checking token's:

- RSA signature
- integrity - to make sure no one tampered with it
- expiration time
- claims like audience, scope, etc.

Additionally it checks if user is permitted to access given API by checking the
`roles` claim in the access token.

Access tokens have an expiration time, after which they're no longer valid, and
a new access token is required. To provide new access token create either a new
connection or use :py:meth:`volue.mesh.Connection.update_external_access_token`.
