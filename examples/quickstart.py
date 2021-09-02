import volue.mesh

# Configure the connection you want
connection = volue.mesh.Connection()

# secure vs not
# kerboros vs not

# Print python api version
python_api_version = 0 #TODO
print(f"Python API version: {python_api_version}")

# Check server version is compatible with python api
compatible = connection.is_server_compatible()
print(f"Servers version is compatible with this version of the API: {compatible}")

# Which version is the server running
mesh_server_version = connection.get_version()
print(f"The connected Volue Mesh Server version is {mesh_server_version}")

# Create a remote session on the Volue Mesh server
connection.start_session()
print("TODO")

# get some data