"""
Tests for running the example scripts
"""

import glob
import os
import socket
import subprocess
import sys

import pytest

from volue import mesh


def is_port_responding(host: str, port: int):
    """Helper function to check if a socket will respond to a connection."""
    args = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    for family, socktype, proto, _, sockaddr in args:
        a_socket = socket.socket(family, socktype, proto)
        try:
            a_socket.connect(sockaddr)
        except socket.error:
            return False
        else:
            a_socket.close()
            return True


@pytest.mark.server
def test_is_grpc_responding(mesh_test_config):
    """Check if the server's socket is open and responding."""
    assert is_port_responding(*mesh_test_config.address.split(":")) is True


@pytest.mark.examples
@pytest.mark.database
def test_example(mesh_test_config, example_path):
    args = [sys.executable, example_path, mesh_test_config.address]
    if mesh_test_config.tls_root_certs is not None:
        args.append(mesh_test_config.tls_root_certs_path)
    subprocess.run(args, check=True, timeout=15)


def pytest_generate_tests(metafunc):
    if "example_path" in metafunc.fixturenames:
        examples = os.path.join(os.path.dirname(mesh.__file__), 'examples')
        paths = glob.glob(examples + "/*.py")
        metafunc.parametrize("example_path", paths)


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
