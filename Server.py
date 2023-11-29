import socket
import threading

clients = []
aliases = []

PUT_OPCODE = '000'
GET_OPCODE = '001'
CHANGE_OPCODE = '010'
SUMMARY_OPCODE = '011'
HELP_OPCODE = '100'


def handle_request_help():
    commandList = ("Possible commands: \n\n'put' to UPLOAD a file\n'get' to DOWNLOAD a file\n'summary' to get the "
                   "maximum, minimum and average of the numbers of the specified file\n'change' to UPDATE the name of "
                   "a specified file\n'help' to receive a list of commands \n'exit' to break connection with server")
    return commandList


# The purpose of this function is to listen to the client's requests and to reply to the client
def handle_client(client):
    while True:
        # try:
        # this 'message' is what the client sent to the server
        message = client.recv(4096).decode()
        print(message)

        reply = handle_request_help()
        client.send(reply.encode('utf-8'))
        # except:
        # index = clients.index(client)
        # client.remove(client)
        # client.close()
        # alias = aliases[index]
        # print(f'{alias} has disconnected from the server')
        # aliases.remove(alias)
        # break


# This is where the initial server creation is made
def main():
    host = '127.0.0.1'
    port = 12000
    # DGRAM = UDP
    # server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # STREAM = TCP
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

        # this thread's sole purpose is to listen to the SPECIFIED client's requests
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()


if __name__ == '__main__':
    main()
