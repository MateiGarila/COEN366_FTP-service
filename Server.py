import socket
import threading

clients = []


def main():
    host = '127.0.0.1'
    port = 12000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print('Server is listening')

    while True:
        conn, addr = server.accept()
        print('Got connection from ', addr)
        message = 'Thank you for connecting'
        conn.send(message.encode())
        conn.close()


if __name__ == '__main__':
    main()

