import glob
import os
import unittest
from tests.test_utilities.server_config import ADDRESS, PORT, SECURE_CONNECTION
from tests.test_utilities.utilities import run_example_script


class TestExamples(unittest.TestCase):

    def test_run_example_scripts(self):
        """Run all example scripts and check if they exit with no error code."""

        examles = os.path.join(os.path.dirname(__file__), '..', 'examples')
        os.chdir(examles)
        for file in glob.glob("*.py"):
            run_example_script(self, file, ADDRESS, PORT, SECURE_CONNECTION)


if __name__ == '__main__':
    unittest.main()
