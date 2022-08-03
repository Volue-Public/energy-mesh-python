import uuid
from volue.mesh.examples import _get_connection_info
from volue.mesh import Connection


def main(address, port, root_pem_certificate):
    """Showing different ways of working with sessions."""

    # Configure the connection you want.
    connection = Connection(address, port, root_pem_certificate)

    # 1. Create a session, open and close session.
    session = connection.create_session()
    session.open()
    print("1. You now have a new open session")
    session.close()

    # 2. Create session using the with statement.
    # Session will be created, opened and closed within the 'with' statement scope
    with connection.create_session() as session:
        print("2. You now have a new open session")

    # 3. Connecting to a potentially open session.
    # Session ids can be found in the session object:
    # session.session_id
    # Note: If the session_id is not the id of an open session,
    # the server will create a new one for you.
    # Set the session id you want to connect to
    session_id = uuid.UUID("123e4567-e89b-12d3-a456-556642440000")
    print(f"3. Session id you want to connect to: {session_id}")
    session = connection.connect_to_session(session_id)
    # Try connecting to that session id, if it does not exist, a new one will be created without warning
    session.open()
    print(
        "3. You have now an open session, either the one you requested or a new one if it did not exist"
    )
    # Check which session you are connected to and close it
    print(f"3. Session id you are to connect to: {session.session_id}")
    session.close()


if __name__ == "__main__":
    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
