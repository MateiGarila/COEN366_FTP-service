import socket
# import os
import sys

PUT_OPCODE = '000'
GET_OPCODE = '001'
CHANGE_OPCODE = '010'
SUMMARY_OPCODE = '011'
HELP_OPCODE = '100'


def get_OPCODE(command_str):
    if command_str == 'put':
        return PUT_OPCODE
    elif command_str == 'get':
        return GET_OPCODE
    elif command_str == 'change':
        return CHANGE_OPCODE
    elif command_str == 'summary':
        return SUMMARY_OPCODE
    elif command_str == 'help':
        return HELP_OPCODE
    else:
        return 'Command not supported'


def get_fileNameLength(fileName):
    numChars = len(fileName)
    if numChars > 31:
        return 'File name not supported'
    else:
        binaryChars = bin(numChars)
        return binaryChars[2:].zfill(5)


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 12000
    client.connect(('127.0.0.1', port))

    # This will have to be transferred to the server-side
    commandList = ("Possible commands: \n\n'put' to UPLOAD a file\n'get' to DOWNLOAD a file\n'summary' to get the "
                   "maximum, minimum and average of the numbers of the specified file\n'change' to UPDATE the name of "
                   "a specified file\n'help' to receive a list of commands \n'exit' to break connection with server")

    alias = input(client.recv(1024).decode())
    alias_message = f'{alias}: {input("")}'
    client.send(alias_message.encode('utf-8'))
    print(client.recv(1024).decode())

    while True:
        choice = input("FTP-Client>")

        command_str = choice.split()
        opcode = get_OPCODE(command_str[0])
        client_send(client, opcode)

        if opcode != 'Command not supported':
            print("Command is supported")

            if opcode == PUT_OPCODE or opcode == GET_OPCODE or opcode == CHANGE_OPCODE:
                fileNameLength = get_fileNameLength(command_str[1])
                print(opcode + fileNameLength)

        if choice == 'help':
            print(commandList)

        if choice == 'exit':
            print("Exit selected")
            client.close()
            sys.exit()


def client_send(client, message):
    client.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
