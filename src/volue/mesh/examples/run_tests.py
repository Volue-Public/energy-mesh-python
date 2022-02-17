import pytest
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.tests import test_timeseries

def main():
    """Showing how to run tests."""

    # Change to fit your server
    sc.DefaultServerConfig.ADDRESS = "localhost"
    sc.DefaultServerConfig.PORT = 50051
    # Note: authentication tests require secure connection,
    # so providing root certificate is required for them.
    sc.DefaultServerConfig.ROOT_CERTIFICATE_PATH = None

    # If Mesh gRPC server is running as a service user,
    # for example LocalSystem, NetworkService or a user account
    # with a registered service principal name then it is enough
    # to provide hostname as service principal, e.g.:
    #   'HOST/hostname.ad.examplecompany.com'
    # If Mesh gRPC server is running as a user account without
    # registered service principal name then it is enough to provide
    # user account name running Mesh server as service principal, e.g.:
    #   'ad\\user.name' or r'ad\user.name'
    # Note: winkerberos converts service principal name if provided in
    #       RFC-2078 format. '@' is converted to '/' if there is no '/'
    #       character in the service principal name. E.g.:
    #           service@hostname
    #       Would be converted to:
    #           service/hostname
    sc.DefaultServerConfig.KERBEROS_SERVICE_PRINCIPAL_NAME = 'HOST/example.companyad.company.com'

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
