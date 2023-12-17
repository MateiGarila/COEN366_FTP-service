import socket
import threading

from server.Server_functions import start_client_tcp, start_client_udp


# This is where the initial server creation is made
def main(ip, port, protocol):
    host = ip
    server_address = (ip, port)

    if protocol == '1':
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen()

        print('Server is listening... TCP')

        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=start_client_tcp, args=(conn, addr))
            thread.start()

    elif protocol == '2':
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((host, port))
        print('Server is listening... UDP')

        while True:
            data, client_address = server_socket.recvfrom(1024)
            message = data.decode()
            print(f"Received request from {client_address}: {message}")
            thread = threading.Thread(target=start_client_udp, args=(server_socket, server_address))
            thread.start()


if __name__ == '__main__':
    main()
