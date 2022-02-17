"""
Examples are written in a way that is meant to show how to use a certain feature of the API.
"""

import sys


def _get_connection_info():
    """Helper function to set hand over connection info to examples."""
    address = "localhost"
    port = 50051
    root_certificate_path = ''

    if len(sys.argv) > 1:
        address = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        root_certificate_path = sys.argv[3]

    return address, port, root_certificate_path
