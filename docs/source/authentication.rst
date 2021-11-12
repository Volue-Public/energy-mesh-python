Authentication
--------------

The Mesh Python SDK supports user authentication/authorization feature. Because every user that is authenticated by Mesh server is also authorized to access all APIs exposed from Mesh gRPC, we will refer to it by just **authentication**.

.. note::
   Authentication is done using Kerberos protocol. Client and server must be in the *line of sight* of the Key Distribution Center (KDC).

If Mesh server is configured to use authentication then only authenticated user may work with Mesh. Authenticated user obtains Mesh access token that is used for each call to Mesh server to prove user's identity.
Only two methods can be called by without authentication:

* AuthenticateKerberos - used for getting authorization token
* GetVersion - for getting Mesh server version

.. note::
   For security reasons authentication requires secure connection with Mesh server (using TLS). It is needed for encrypting tokens.


Usage
*****************

To use authentication user has to provide authentication parameters when creating :ref:`volue.mesh`.Connection or :ref:`volue.mesh.aio`.Connection: object.
Authentication parameters consist of:

* Service Principal Name (SPN)
* User Principal Name (UPN)

Depending on the system configuration providing only *service principal* may be enough for successful authentication.

Instantiation of Connection object with authentication parameters will perform authentication process and obtain Mesh token that will be used for each subsequent call to Mesh server.


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

Mesh token is valid for 1 hour, after this time it will expire and a new token needs to be obtained from Mesh server. This is done automatically and user does not need to take any additional action.

User may optionally revoke Mesh access token. This may useful when a user finishes working with Mesh and wants to make sure it will not be used by anyone else for the time until it expires.


Requirements
*****************

#. Configure Mesh server to use authentication and TLS:

   .. code-block:: javascript

      Configuration.Network.GRPC.SetEnabled(true);
      Configuration.Network.GRPC.EnableKerberos(true);
      Configuration.Network.GRPC.EnableTLS(true);

#. Find out correct *service principal* for Mesh server you want to connect to.
#. Create :ref:`volue.mesh`.Connection or :ref:`volue.mesh.aio`.Connection: object with authentication parameters.


Example
**********************************

Please refer to example *authorization.py*:

.. literalinclude:: /../../src/volue/mesh/examples/authorization.py


