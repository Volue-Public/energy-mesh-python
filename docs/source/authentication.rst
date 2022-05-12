==============
Authentication
==============

When connecting to Mesh using the Python SDK you might need to authenticate
using Kerberos. This is required by the Mesh server if Kerberos is enabled
for the gRPC interface in the Mesh configuration file.

For security reasons authentication also requires TLS to be enabled, and
you might therefore need Mesh's TLS certificate in the below examples.


Windows Kerberos
****************

If you are on Windows as an Active Directory domain user Kerberos
authentication is relatively simple. You only need to find the service
principal name the Mesh service is running under. If Mesh is running as a
machine user the service principal name will usually be
``HOST/full.qualified.domain.name`` or ``HOST/f.q.d.n@DOMAIN.COM`` but it might
be different in your environment. Determining the service principal name for
the Mesh service is out of scope for this guide.

.. code-block:: python

	from volue import mesh

	with open("certificate.pem", "rb") as f:
	    certificate = f.read()

	connection = mesh.Connection.with_kerberos("mesh.local:50051", certificate,
					           "HOST/mesh.local@DOMAIN.COM", "user@DOMAIN.COM")
	print(connection.get_user_identity())


MIT Kerberos (Linux/MacOS)
**************************

When running on Linux or MacOS our world quickly becomes more complicated.
In most configurations the system will not be aware of the Active Directory
configuration, and you will not be logged in as a domain user. We therefore
have to complete a number of steps to make Kerberos credentials available
to the Python SDK.

This is a quickstart guide designed to help you get started, but MIT Kerberos
and Active Directory are both complex topics with numerous possible
configurations, and it is not unlikely that you will need to do some debugging
at one or more of the steps below.

Before we get started you'll need to find the network address(es) of the Active
Directory (AD) Key Distribution Center (KDC), the AD domain name, credentials
for your AD user, the service principal name for the Mesh service, and the TLS
certificate of the Mesh server. Your IT/Operations department might be able to
assist with this, or you can try to investigate yourself.

In this guide we're going to assume that the domain name also resolves to the
domain controller and the KDC.

To get the domain name from a domain joined Windows computer::

	REM Get the AD domain name.

	> set USERDNSDOMAIN
	USERDDNSOMAIN=DOMAIN.COM

	REM Get a bit more information about the domain controller.
	REM You should note down the IP address here.

	> nltest /dsgetdc:DOMAIN.COM
	...

At this stage it's a good idea to test if the domain controller is reachable
from your Linux machine. All the following Linux examples run on Ubuntu 20.04
LTS::

	# Ideally your DNS setup includes the domain controller. This will
	# make the following steps significantly easier. If this command
	# fails it might be a good idea to add the IP address of the
	# domain controller(s) to your list of DNS servers.

	$ ping domain.com       # Or the address of a domain controller.

	# You can also use the IP directly, but we would recommend against
	# it.

	$ ping 172.20.101.20

If the above commands both failed, your network will not allow Kerberos
authentication, and you will have to resolve your network issues.

Then we should see if we're able to connect to the KDC on the Kerberos port. By
default the Kerberos protocol will communicate on port 88. If this fails you
will have to work with your IT/Operations department to resolve the issue::

	$ netcat -vz domain.com 88
	Connection to domain.com 88 port [tcp/kerberos] succeeded!

If everything has gone well up until this point it's time to install MIT
Kerberos. On your distribution the MIT Kerberos package names might be different::

	$ sudo apt install krb5-user krb-config libkrb5-dev

Then we'll need to configure MIT Kerberos::

	$ cat /etc/krb5.conf
	[libdefaults]
        	default_realm = DOMAIN.COM

	[realms]
        	DOMAIN.COM = {
                	kdc = domain.com
                	admin_server = domain.com
		}

	[domain_realm]
        	.domain.com = DOMAIN.COM
        	domain.com = DOMAIN.COM

And finally we can get a ticket granting ticket from the KDC. If this
works you've successfully performed your first Kerberos authentication::

	$ kinit -V user@DOMAIN.COM
	Using default cache: /tmp/krb5cc_1000
	Using principal: user@DOMAIN.COM
	Password for user@DOMAIN.COM: ****
	Authenticated to Kerberos v5

The newly generated ticket granting ticket will be used when the Mesh
Python SDK authenticates to the Mesh server. As long as that ticket is
available on the client you will not have to retype your password.
To destroy the ticket run ``kdestroy``.

Finally, we can connect to the Mesh server from Python.

.. code-block:: python

	from volue import mesh

	# Most certificates won't work with IP addresses, therefore
	# you'll need to be able to resolve the Mesh server by name,
	# either through your DNS configuration, or through /etc/hosts.
	with open("certificate.pem", "rb") as f:
	    certificate = f.read()

	# mesh.domain.com is the address of the Mesh server.
	# HOST/... is the service principal name, and user@DOMAIN.COM
	# is the user principal name.
	connection = mesh.Connection.with_kerberos(
	    "mesh.domain.com:50051", certificate,
	    "HOST/mesh.domain.com@DOMAIN.COM", "user@DOMAIN.COM"
	)
	print(connection.get_user_identity())


Example
*******

Please refer to example *authorization.py*:

.. literalinclude:: /../../src/volue/mesh/examples/authorization.py


Internals
*********

Mesh authentication is based on **authorization tokens**. When authentication
is enabled most network calls to Mesh will require one of these tokens to
succeed. To get an authorization token the client is required to make a call
to an authentication endpoint, such as the ``AuthenticateKerberos`` gRPC
method. Authentication endpoints perform the necessary authentication steps,
and if successful return an authorization token that can be used for future
calls.

Authorization tokens have an expiration time, after which they're no longer
valid, and a new authentication call and a new token is required. At the
time of writing most authorization tokens are valid for one hour, but this
is subject to change.

When creating a Mesh connection with authentication enabled in the Python SDK
authentication calls and authorization tokens will be handled transparently
through the ``_authentication`` module. This module will perform authentication
calls when a new token is required, and add authorization tokens to calls
that require them.
