import glob
import os
import pytest
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.tests.test_utilities.utilities import run_example_script, is_port_responding
import volue.mesh


@pytest.mark.server
def test_is_grpc_responding():
    """Check if the servers socket is open and responding."""
    assert is_port_responding(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT) is True


@pytest.mark.examples
@pytest.mark.database
def test_run_example_scripts():
    """Check if all examples runs and that they exit with no error code."""

    examples = os.path.join(os.path.dirname(volue.mesh.__file__), 'examples')
    os.chdir(examples)
    for file in glob.glob("*.py"):
        run_example_script(file, sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)


if __name__ == '__main__':
    pytest.main()
