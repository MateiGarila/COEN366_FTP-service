import socket
import threading

def handle_client_tcp(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        received_message = data.decode('utf-8')
        print(f"Received request from client: {received_message}")

        # Echo the received message back to the client
        client_socket.sendall(data)

    client_socket.close()

def tcp_server():
    server_address = ('127.0.0.1', 12345)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(server_address)
    server_socket.listen()

    print('Server is listening... TCP')

    while True:
        client_socket, client_address = server_socket.accept()
        print(f'TCP Connection established with {str(client_address)}')

        thread = threading.Thread(target=handle_client_tcp, args=(client_socket,))
        thread.start()

def tcp_client():
    server_address = ('127.0.0.1', 12345)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    message_to_send = "hi"
    client_socket.sendall(message_to_send.encode('utf-8'))

    data = client_socket.recv(1024)
    received_message = data.decode('utf-8')
    print(f"Received response from server: {received_message}")

    client_socket.close()

if __name__ == "__main__":
    # Start the server in a separate thread
    server_thread = threading.Thread(target=tcp_server)
    server_thread.start()

    # Allow some time for the server to start before starting the client
    import time
    time.sleep(1)

    # Run the client
    tcp_client()

    # Wait for the server thread to complete before exiting
    server_thread.join()
