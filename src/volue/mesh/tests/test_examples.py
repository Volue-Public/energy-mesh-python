from volue.mesh.tests.test_utilities.server_config import ADDRESS, PORT, SECURE_CONNECTION
from volue.mesh.tests.test_utilities.utilities import run_example_script, is_port_responding
import volue.mesh

import glob
import os
import unittest
import pytest


@pytest.mark.server
def test_is_grpc_responding():
    assert is_port_responding(ADDRESS, PORT) is True


@pytest.mark.database
def test_run_example_scripts():
    """Run all example scripts and check if they exit with no error code."""

    examples = os.path.join(os.path.dirname(volue.mesh.__file__), 'examples')
    os.chdir(examples)
    for file in glob.glob("*.py"):
        run_example_script(file, ADDRESS, PORT, SECURE_CONNECTION)


if __name__ == '__main__':
    unittest.main()
