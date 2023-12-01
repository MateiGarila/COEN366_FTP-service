import socket
import threading
import util

clients = []
aliases = []

PUT_OPCODE = '000'
GET_OPCODE = '001'
CHANGE_OPCODE = '010'
SUMMARY_OPCODE = '011'
HELP_OPCODE = '100'
HELP_RESPONSE = '110'


def handle_request_help():
    commandList = "Commands are: exit change get help put summary"
    commandInBits = util.get_binary_string(commandList)
    commandBytes = len(commandInBits) // 8
    bytesInBits = bin(commandBytes)[2:]
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
            server_send(client, handle_request_help())


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
