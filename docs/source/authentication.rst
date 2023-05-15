=====================
Client authentication
=====================

Mesh server could be configured to protect its gRPC API so that only
authenticated users that are assigned to specific roles can access it. There
are two options:

  - **Kerberos**, where Mesh authenticates users and grants access to specific
    APIs based on what AD groups the authenticated users belong to.
  - **External access token**, where users authenticate and request access to
    Mesh from external authorization servers, and Mesh validates the access
    token that is obtained from the authorization server.

.. toctree::
   :maxdepth: 2

   kerberos
   external_auth
