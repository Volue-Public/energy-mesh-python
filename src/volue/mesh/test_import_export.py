import threading
import time
import subprocess

def main():
    mesh_exe = ['C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug/Powel.Mesh.Server.exe']

    with subprocess.Popen(mesh_exe) as mesh_proc:
        imp_exp_exe = 'C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug/Powel.Mesh.Model.ImportExport.exe'
        imp_exp_args = [imp_exp_exe, '-i', 'base_dump.mdump', '-S']

        # Import the base data first
        subprocess.check_call(imp_exp_args)

        # Set validity for an object (Models->MeshTEK->Mesh->To_Areas->Finland)

        # start_session()
        # set_validity()
        # commit()
        # end_session()
        # export_data_with_validity()

        mesh_proc.terminate()

    with subprocess.Popen(mesh_exe) as mesh_proc:
        # start_session()
        # import_data_with_validity()
        # get_validity()
        # end_session()
        # check_validity()

if __name__ == '__main__':
    main()
