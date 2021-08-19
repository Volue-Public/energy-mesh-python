import subprocess
import sys
import asyncio


def run_example_script(test, path):
    p = subprocess.Popen(
        [sys.executable, path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (stdoutdata, stderrdata) = p.communicate()
    exit_code = p.returncode
    test.assertEqual(exit_code, 0)


# Helper function to allow us to use same test for async and sync connection
def await_if_async(coroutine):
    if asyncio.iscoroutine(coroutine):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coroutine)
    return coroutine
