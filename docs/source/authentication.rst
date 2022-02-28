Authentication
--------------

The Mesh Python SDK supports user authentication/authorization feature. Because every user that is authenticated by Mesh server is also authorized to access all APIs exposed from Mesh gRPC, we will refer to it by just **authentication**.

.. note::
   Authentication is done using the Kerberos protocol towards Active Directory. Client and server must be in *line of sight* of the Key Distribution Center (KDC).

If the Mesh server is configured to use authentication then only authenticated users may work with Mesh. Authenticated users obtain Mesh access tokens that are used for each call to Mesh server to prove the user's identity.
Only two methods can be called without access token:

* AuthenticateKerberos - used for getting authorization token
* GetVersion - for getting Mesh server version

.. note::
   For security reasons authentication requires secure connection with Mesh server (using TLS). It is needed for encrypting tokens.


Usage
*****************

To use authentication the user has to provide authentication parameters when creating a :ref:`volue.mesh`.Connection or a :ref:`volue.mesh.aio`.Connection:.
Authentication parameters consist of:

* Service Principal Name (SPN)
* User Principal Name (UPN)

Depending on the system configuration providing only *service principal* may be enough for successful authentication. This is usually the case when authenticating as the currently logged in Windows user.

Instantiation of a Connection object with authentication parameters will perform the authentication process and obtain a Mesh token that will be used for each subsequent call to the Mesh server.


Service Principal
*****************

If Mesh gRPC server is running as a service user, for example LocalSystem, NetworkService or a user account with a registered service principal name then it is enough to provide hostname as service principal, e.g.:

   .. code-block:: python

      'HOST/hostname.ad.examplecompany.com'

If Mesh gRPC server is running as a user account without registered service principal name then it is enough to provide user account name running Mesh server as service principal, e.g.:

   .. code-block:: python

      'ad\\user.name'

   Or:

   .. code-block:: python

      r'ad\user.name'

.. note::
    Winkerberos converts service principal name if provided in RFC-2078 format. '@' is converted to '/' if there is no '/' character in the service principal name.

    E.g.: **service@hostname**

    Would be converted to: **service/hostname**


Mesh token
*****************

The Mesh access token is valid for 1 hour, after this time it will expire and a new token needs to be obtained from the Mesh server. This is done automatically and the user does not need to take any additional action.

The user may optionally revoke the Mesh access token. This may useful when a user finishes working with Mesh and wants to make sure it will not be used by anyone else for the time until it expires.


Requirements
*****************

#. Mesh server configured to use authentication and TLS. Please contact Volue consultant to confirm your server configuration.
#. Find out correct *service principal* for Mesh server you want to connect to.
#. Create a :ref:`volue.mesh`.Connection or a :ref:`volue.mesh.aio`.Connection: object with authentication parameters.


Example
**********************************

Please refer to example *authorization.py*:

.. literalinclude:: /../../src/volue/mesh/examples/authorization.py


