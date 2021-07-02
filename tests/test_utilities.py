import subprocess
import sys
import asyncio


def can_talk_to_mesh_health_point(host, port) -> bool:
    # TODO implement
    return False

def powel_mesh_service_is_running_locally() -> bool:
    mesh_health_port = None
    return can_talk_to_mesh_health_point('localhost', mesh_health_port)


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
