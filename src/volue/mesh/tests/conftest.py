"""pytest command line options and global test fixtures."""

import typing
from dataclasses import dataclass

import pytest
import pytest_asyncio

import volue.mesh.aio
from volue import mesh


# pytest magically runs this to add command line options.
def pytest_addoption(parser):
    parser.addoption(
        "--address",
        metavar="ADDRESS",
        default="localhost:50051",
        help="the Mesh server address. Default localhost:50051.",
    )
    parser.addoption(
        "--creds-type",
        default="insecure",
        choices=["insecure", "tls", "kerberos"],
        help="the connection credential type. Default insecure.",
    )
    parser.addoption(
        "--tls-root-certs",
        metavar="FILE",
        default=None,
        help="use this PEM formatted root certificate chain file.",
    )
    parser.addoption(
        "--kerberos-service-principal",
        metavar="PRINCIPAL",
        default=None,
        help="use this service principal name for Kerberos authentication.",
    )
    parser.addoption(
        "--kerberos-user-principal",
        metavar="PRINCIPAL",
        default=None,
        help="use this client principal for Kerberos authentication.",
    )


@dataclass(init=False)
class TestConfig:
    address: str
    creds_type: str
    tls_root_pem_certs_path: typing.Optional[str]
    tls_root_pem_certs: typing.Optional[bytes]
    krb5_svc: typing.Optional[str]
    krb5_usr: typing.Optional[str]

    def __init__(self, config):
        self.address = config.getoption("--address")
        self.creds_type = config.getoption("--creds-type")
        self.tls_root_pem_certs_path = config.getoption("--tls-root-certs")
        self.krb5_svc = config.getoption("--kerberos-service-principal")
        self.krb5_usr = config.getoption("--kerberos-user-principal")

        if self.creds_type != "kerberos":
            if self.krb5_svc is not None:
                raise pytest.UsageError(
                    "--kerberos-service-principal can only be used for --creds-type=kerberos connections"
                )
            if self.krb5_usr is not None:
                raise pytest.UsageError(
                    "--kerberos-user-principal can only be used for --creds-type=kerberos connections"
                )

        if self.creds_type == "insecure":
            if self.tls_root_pem_certs_path:
                raise pytest.UsageError(
                    "--tls-root-certs cannot be used for --creds-type=insecure connections"
                )

        if self.tls_root_pem_certs_path is not None:
            with open(self.tls_root_pem_certs_path, "rb") as f:
                self.tls_root_pem_certs = f.read()
        else:
            self.tls_root_pem_certs = None


_test_config: typing.Optional[TestConfig] = None


# pytest magically runs this after parsing the command line.
def pytest_configure(config) -> None:
    global _test_config
    _test_config = TestConfig(config)


@pytest.fixture(scope="session")
def mesh_test_config() -> TestConfig:
    """Returns the TestConfig of this test session.

    Generally tests should use the connection, session, async_connection and async_session
    fixtures to connect to Mesh, but in cases where explicit handling of connections is
    necessary, such as authentication tests, this can be used instead.
    """
    return _test_config


@pytest.fixture(scope="session")
def connection() -> mesh.Connection:
    """Return a global :class:`mesh.Connection` for the test session.

    In 99% of use cases a mesh.Connection can be treated as stateless. It is therefore fine
    to reuse the connection across _most_ tests. The cases where the connection cannot be used
    as stateless are those where authentication tokens are explicitly manipulated. In those
    cases this fixture should not be used.
    """
    if _test_config.creds_type == "insecure":
        return mesh.Connection.insecure(_test_config.address)
    elif _test_config.creds_type == "tls":
        return mesh.Connection.with_tls(
            _test_config.address, _test_config.tls_root_pem_certs
        )
    elif _test_config.creds_type == "kerberos":
        return mesh.Connection.with_kerberos(
            _test_config.address,
            _test_config.tls_root_pem_certs,
            _test_config.krb5_svc,
            _test_config.krb5_usr,
        )


@pytest.fixture
def session(connection: mesh.Connection) -> mesh.Connection.Session:
    """Return a :class:`mesh.Connection.Session` for the current test.

    The session will be closed after the test is complete.

    This fixture uses a global connection, see :func:`connection` above for more information.
    """
    with connection.create_session() as session:
        yield session


@pytest.fixture
def async_connection():
    """Return a :class:`mesh.aio.Connection` for the current test."""
    if _test_config.creds_type == "insecure":
        return mesh.aio.Connection.insecure(_test_config.address)
    elif _test_config.creds_type == "tls":
        return mesh.aio.Connection.with_tls(
            _test_config.address, _test_config.tls_root_pem_certs
        )
    elif _test_config.creds_type == "kerberos":
        return mesh.aio.Connection.with_kerberos(
            _test_config.address,
            _test_config.tls_root_pem_certs,
            _test_config.krb5_svc,
            _test_config.krb5_usr,
        )


@pytest_asyncio.fixture
async def async_session(async_connection):
    """Return a :class:`mesh.aio.Connection.Session` for the current test.

    The session will be closed after the test is complete.
    """
    async with async_connection.create_session() as session:
        yield session
