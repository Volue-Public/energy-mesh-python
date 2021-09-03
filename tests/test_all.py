import glob, os
from test_timeseries import *
from test_session import *
import server_config as sc

class RunExamples(unittest.TestCase):

    def test_run_example_scripts(self):
        """Run all example scripts and check if they exit with no error code."""

        os.chdir("../examples/")
        for file in glob.glob("*.py"):
            run_example_script(self, file, sc.ADDRESS, sc.PORT, sc.SECURE_CONNECTION)


if __name__ == '__main__':
    unittest.main()
