import threading
from server.Server import main as start_server
from client.Client import main as start_client

# Entry point for the script
if __name__ == '__main__':
    # Start the server and client in separate threads
    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)

    # Start the server and client threads
    server_thread.start()
    client_thread.start()

    # wait for both threads to finish
    server_thread.join()
    client_thread.join()
