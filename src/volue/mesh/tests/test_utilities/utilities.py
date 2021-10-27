from volue.mesh import Timeseries
import pyarrow as pa
from datetime import datetime
import uuid
import subprocess
import sys
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
    """Helper function to run an example script."""
    p = subprocess.Popen(
        [sys.executable, path, address, str(port), str(secure_connection)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdoutdata, stderrdata = p.communicate()
    exit_code = p.returncode
    assert exit_code == 0, f"{stderrdata} {stdoutdata}"


def get_test_data():
    arrays = [
        pa.array([1462060800, 1462064400, 1462068000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    timskey = 201503
    uuid_id = uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e")
    start_time = datetime(2016, 5, 1)
    end_time = datetime(2016, 5, 14)
    return end_time, start_time, table, timskey, uuid_id
