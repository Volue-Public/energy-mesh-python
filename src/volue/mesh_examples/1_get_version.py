from __future__ import print_function
import logging

from volue.mesh.client import mesh_client

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.
    version_info = mesh_client.get_version_string()
    logging.info(version_info)
