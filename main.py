# main_script.py


# Import the necessary modules and functions
import socket
import threading
import time
from server.Server import main as start_server
from client.Client import main as start_client

# Entry point for the script
if __name__ == '__main__':
    # Assuming you want to start the server and client in separate threads
    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)

    # Start the server and client threads
    server_thread.start()
    client_thread.start()

    # Optionally, you can wait for both threads to finish
    server_thread.join()
    client_thread.join()
