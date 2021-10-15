import pytest
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.tests import test_timeseries

def main():
    """Showing how to run tests."""

    # Change to fit your server
    sc.DefaultServerConfig.ADDRESS = "localhost"
    sc.DefaultServerConfig.PORT = 50051
    sc.DefaultServerConfig.SECURE_CONNECTION = False

    # Run individual tests:
    test_timeseries.test_can_create_empty_timeserie()

    # Run a subset (or all) tests and generate report:
    cmd = [
        '--junitxml', 'test.xml',       # the test report
        '-ra',                          # specify which tests should be reported
        '-vv',                          # verbose output
        '--pyargs', 'volue.mesh.tests', # specify that it is the volue.mesh.tests that will run
        '-m', 'unittest or server'      # which subset of tests to run
    ]
    # pytest.main(cmd) # uncomment this to run


if __name__ == "__main__":
    main()
