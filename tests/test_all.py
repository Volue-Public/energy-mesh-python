import unittest

from test_utilities import *
from test_timeseries import *
from test_session import *


class RunExamples(unittest.TestCase):

    # TODO Automate generation of example script running

    def test_1_get_version(self):
        run_example_script(self, "../examples/mesh/1_get_version.py")

    def test_2a_get_timeseries_points(self):
        run_example_script(self, "../examples/mesh/2a_get_timeseries_points.py")

    def test_2b_get_timeseries_points_async(self):
        run_example_script(self, "../examples/mesh/2b_get_timeseries_points_async.py")

    def test_3a_edit_timeseries_points(self):
        run_example_script(self, "../examples/mesh/3a_edit_timeseries_points.py")

    def test_3b_edit_timeseries_points_async(self):
        run_example_script(self, "../examples/mesh/3b_edit_timeseries_points_async.py")


if __name__ == '__main__':
    unittest.main()
