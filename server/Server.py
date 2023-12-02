import socket
import threading

from ftp_functions.ftp_functions import (
    get_binary_string
)
from ftp_constants import (
    PUT_OPCODE,
    GET_OPCODE,
    CHANGE_OPCODE,
    SUMMARY_OPCODE,
    HELP_OPCODE,
    HELP_RESPONSE
)

clients = []
aliases = []


def handle_request_help():
    # commandList the way it is now is exactly 31 bytes long. Which is the maximum allowed to be transferred to the user
    commandList = "bye change get help put summary"
    commandInBits = get_binary_string(commandList)
    commandBytes = len(commandInBits) // 8
    bytesInBits = bin(commandBytes)[2:].zfill(5)
    return HELP_RESPONSE + bytesInBits + commandInBits


# The purpose of this function is to listen to the client's requests and to reply to the client
def handle_client(client):
    while True:
        # this 'message' is what the client sent to the server
        message = client.recv(4096).decode()
        print(message)
        opcode = message[:3]
        message = message[3:]
        print("Opcode: " + opcode)
        print("Message: " + message)

        if opcode == PUT_OPCODE:
            print("PUT")
        elif opcode == GET_OPCODE:
            print("GET")
        elif opcode == CHANGE_OPCODE:
            print("CHANGE")
        elif opcode == SUMMARY_OPCODE:
            print("SUMMARY")
        elif opcode == HELP_OPCODE:
            help_string = handle_request_help()
            server_send(client, help_string)


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


# This method is used to send information to the client
def server_send(server, message):
    server.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
