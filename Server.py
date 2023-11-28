import socket
import threading

clients = []
aliases = []


def handle_client(client):
    while True:
        try:
            # this 'message' is what the client sent to the server
            message = client.recv(4096).decode()
            print(message)
        except:
            index = clients.index(client)
            client.remove(client)
            client.close()
            alias = aliases[index]
            aliases.remove(alias)
            break


def main():
    host = '127.0.0.1'
    port = 12000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print('Server is listening')

    while True:
        conn, addr = server.accept()
        print(f'Connection has been established with {str(addr)}')
        conn.send('What is your alias user? '.encode('utf-8'))
        alias = conn.recv(1024).decode()
        aliases.append(alias)
        clients.append(conn)
        print('The alias of this client is: ' + alias)
        conn.send(('Thank you for connecting ' + alias + '!').encode('utf-8'))
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()


if __name__ == '__main__':
    main()
