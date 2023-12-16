import socket
import threading
import time

def handle_client_udp(client_socket):
    data, server_address = client_socket.recvfrom(1024)
    received_message = data.decode('utf-8')
    print(f"Received request from {server_address}: {received_message}")

    # You can add more client-specific logic here if needed

    client_socket.close()

def handle_server_udp(server_socket):
    while True:
        data, client_address = server_socket.recvfrom(1024)
        received_message = data.decode('utf-8')
        print(f"Received request from {client_address}: {received_message}")

        # Echo the received message back to the client
        server_socket.sendto(data, client_address)

def udp_server():
    server_address = ('127.0.0.1', 12345)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    print('Server is listening... UDP')

    # Start a separate thread to handle incoming requests
    server_handler_thread = threading.Thread(target=handle_server_udp, args=(server_socket,))
    server_handler_thread.start()

    # Wait for the server handler thread to complete before exiting
    server_handler_thread.join()

def udp_client():
    server_address = ('127.0.0.1', 12345)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_to_send = "hi"
    client_socket.sendto(message_to_send.encode('utf-8'), server_address)

    handle_client_udp(client_socket)

if __name__ == "__main__":
    # Start the server in a separate thread
    server_thread = threading.Thread(target=udp_server)
    server_thread.start()

    # Allow some time for the server to start before starting the client
    time.sleep(1)

    # Run the client
    udp_client()

    # Wait for the server thread to complete before exiting
    server_thread.join()
