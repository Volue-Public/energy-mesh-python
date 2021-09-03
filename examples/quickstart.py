import sys
if len(sys.argv) > 1:
    address = sys.argv[1]
    port = int(sys.argv[2])
    secure_connection = sys.argv[3] == "True"


import volue.mesh

# Configure the connection you want
connection = volue.mesh.Connection(address, port, secure_connection)

# Which version is the server running
mesh_server_version = connection.get_version()
print(f"The connected Volue Mesh Server version is {mesh_server_version}")

# Create a remote session on the Volue Mesh server
connection.start_session()

print("You have now a open session and can request timeseries")

# Close the remote session
connection.end_session()
