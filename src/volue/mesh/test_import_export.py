import threading
import time
import subprocess

from volue import mesh


def main():
    connection = mesh.Connection.insecure("localhost:50051")

    mesh_build_path = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug"
    mesh_exe = f"{mesh_build_path}/Powel.Mesh.Server.exe"
    imp_exp_exe = f"{mesh_build_path}/Powel.Mesh.Model.ImportExport.exe"
    dump_with_validity_path = "C:/Users/martin.galvan/with_validity.mdump"

    print('[MARTIN] Starting mesh...')

    with subprocess.Popen([mesh_exe]) as mesh_proc:
        # Give mesh some time to finish starting up
        time.sleep(10)

        imp_args = [imp_exp_exe, "-i", "C:/Users/martin.galvan/base_dump.mdump", "-S"]

        # Import the base data first
        print('[MARTIN] Importing base data...')

        subprocess.check_call(imp_args)

        # Set validity for an object (Models->MeshTEK->Mesh->To_Areas->Finland)
        with connection.create_session() as session:
            # set_validity()
            session.commit()

        exp_args = [imp_exp_exe, '-o', dump_with_validity_path, "-m", "MeshTEK"]

        # Export data with validity
        print('[MARTIN] Exporting data with validity...')

        subprocess.check_call(exp_args)

        print('[MARTIN] Terminating mesh...')

        mesh_proc.terminate()

    print('[MARTIN] Starting mesh...')

    with subprocess.Popen(mesh_exe) as mesh_proc:
        # Give mesh some time to finish starting up
        time.sleep(10)

        imp_args = [imp_exp_exe, "-i", dump_with_validity_path, "-S"]

        # Import the data with validity
        print('[MARTIN] Importing data with validity...')

        subprocess.check_call(imp_args)

        with connection.create_session() as session:
            pass
            # get_validity()

        print('[MARTIN] Terminating mesh...')

        mesh_proc.terminate()

    # check_validity()


if __name__ == "__main__":
    main()
