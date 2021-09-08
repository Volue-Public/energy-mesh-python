import glob
import os
import unittest
from server_config import ADDRESS, PORT, SECURE_CONNECTION
from test_utilities import run_example_script


class RunExamples(unittest.TestCase):

    def test_run_example_scripts(self):
        """Run all example scripts and check if they exit with no error code."""

        os.chdir("../examples/")
        for file in glob.glob("*.py"):
            run_example_script(self, file, ADDRESS, PORT, SECURE_CONNECTION)


if __name__ == '__main__':
    unittest.main()
