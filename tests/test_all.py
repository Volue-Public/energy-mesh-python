import glob, os
from test_session import *
from test_timeseries import *


class RunExamples(unittest.TestCase):

    def test_run_example_scripts(self):
        """Run all example scripts and check if they exit with no error code."""

        os.chdir("../examples/")
        for file in glob.glob("*.py"):
            run_example_script(self, file)


if __name__ == '__main__':
    unittest.main()
