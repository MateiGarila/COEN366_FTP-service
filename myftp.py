import threading

from server.Server import main as start_server
from client.Client import main as start_client

ip = None
port = None
protocol = None


def get_user_input():
    global ip, port, protocol
    print("myftp> Enter server IP address:")
    ip = input("myftp> ")
    print("myftp> Enter port number:")
    port = int(input("myftp> "))
    print("myftp> Press 1 for TCP, Press 2 for UDP")
    protocol = input("myftp> ")


if __name__ == '__main__':
    get_user_input()
    # TCP testing
    # ip = '127.0.0.1'
    # port = 12000
    # protocol = '2'

    # UDP testing
    # ip = '127.0.0.2'
    # port = 11000
    # protocol = '2'

    # Start the server and client in separate threads
    server_thread = threading.Thread(target=start_server, args=(ip, port, protocol))
    client_thread = threading.Thread(target=start_client, args=(ip, port, protocol))

    # Start the server and client threads
    server_thread.start()
    client_thread.start()

    # wait for both threads to finish
    server_thread.join()
    client_thread.join()
