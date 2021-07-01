import unittest

from test_utilities import *
from timeseries_tests import *
from session_tests import *


class RunExamples(unittest.TestCase):

    # TODO Automate generation of example script running

    @unittest.skipUnless(powel_mesh_service_is_running_locally(), "Powel.Mesh.Server.exe is not running locally")
    def test_1_get_version(self):
        run_example_script(self, "../examples/mesh/1_get_version.py")

    @unittest.skipUnless(powel_mesh_service_is_running_locally(), "Powel.Mesh.Server.exe is not running locally")
    def test_2a_get_timeseries_points(self):
        run_example_script(self, "../examples/mesh/2a_get_timeseries_points.py")

    @unittest.skipUnless(powel_mesh_service_is_running_locally(), "Powel.Mesh.Server.exe is not running locally")
    def test_2b_get_timeseries_points_async(self):
        run_example_script(self, "../examples/mesh/2b_get_timeseries_points_async.py")

    @unittest.skipUnless(powel_mesh_service_is_running_locally(), "Powel.Mesh.Server.exe is not running locally")
    def test_3a_edit_timeseries_points(self):
        run_example_script(self, "../examples/mesh/3a_edit_timeseries_points.py")

    @unittest.skipUnless(powel_mesh_service_is_running_locally(), "Powel.Mesh.Server.exe is not running locally")
    def test_3b_edit_timeseries_points_async(self):
        run_example_script(self, "../examples/mesh/3b_edit_timeseries_points_async.py")


if __name__ == '__main__':
    unittest.main()
