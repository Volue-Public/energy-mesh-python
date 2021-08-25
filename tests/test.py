import volue.mesh

connection = volue.mesh.Connection(host="tdtrhsmgtrunka2.voluead.volue.com", port="500051")

print(connection.get_version())