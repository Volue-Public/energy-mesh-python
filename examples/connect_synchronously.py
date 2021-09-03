import volue.mesh


def get_version(connection):
    # Sending a request to the server, want to know its version
    print("1. Requesting server version")
    version = connection.get_version()
    print(f"2. Server version is {version.version}")


def start_and_end_session(connection):
    print("A. Starting session")
    connection.start_session()
    print("B. Ending session")
    connection.end_session()


def main():
    # Creating a connection, but not sending any requests yet
    connection = volue.mesh.Connection()
    get_version(connection)
    start_and_end_session(connection)

main()
print("Done")

# Outputs:
# 1. Requesting server version
# 2. Server version is 1.12.5.0-dev
# A. Starting session
# B. Ending session
# Done
