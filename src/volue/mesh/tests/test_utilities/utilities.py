import subprocess
import sys
import asyncio
import socket


def is_port_responding(host: str, port: int):
    """Helper function to check if a socket will respond to a connect."""
    args = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    for family, socktype, proto, canonname, sockaddr in args:
        s = socket.socket(family, socktype, proto)
        try:
            s.connect(sockaddr)
        except socket.error:
            return False
        else:
            s.close()
            return True


def run_example_script(path, address, port, secure_connection):
    """Helper function to run a example script."""
    p = subprocess.Popen(
        [sys.executable, path, address, str(port), str(secure_connection)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdoutdata, stderrdata = p.communicate()
    exit_code = p.returncode
    assert exit_code == 0, f"{stderrdata} {stdoutdata}"


def await_if_async(coroutine):
    """Helper function to allow us to use same test for async and sync connection"""
    if asyncio.iscoroutine(coroutine):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coroutine)
    return coroutine
