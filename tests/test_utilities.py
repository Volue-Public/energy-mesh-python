import subprocess
import sys
import asyncio


def powel_mesh_service_is_running_locally() -> bool:
    process_name = "Powel.Mesh.Server.exe"
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    output = subprocess.check_output(call).decode('windows-1252')
    return output.find(process_name) != -1


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
