import socket
# import os
import sys
import threading
import time

PUT_OPCODE = '000'
GET_OPCODE = '001'
CHANGE_OPCODE = '010'
SUMMARY_OPCODE = '011'
HELP_OPCODE = '100'


def handle_server(server):
    while True:
        message = server.recv(4096).decode()
        print(message)


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


def get_fileName_length(fileName):
    numChars = len(fileName)
    if numChars > 31:
        return 'File name not supported'
    else:
        binaryChars = bin(numChars)
        return binaryChars[2:].zfill(5)


def get_fileName_binary(fileName, fileNameLength):
    numBits = int(fileNameLength) * 8
    binary_string = ''.join([bin(ord(c))[2:].zfill(8) for c in fileName])
    return binary_string.zfill(numBits)


def get_string_from_binary(binaryStr):
    binary_bytes = bytearray(int(binaryStr[i:i + 8], 2) for i in range(0, len(binaryStr), 8))
    file_name = ""
    for byte in binary_bytes:
        if byte != 0:
            file_name += chr(byte)
    return file_name

def main():
    # DGRAM = UDP
    # client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # STREAM = TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 12000
    client.connect(('127.0.0.1', port))

    alias = input(client.recv(1024).decode())
    alias_message = f'{alias}: {input("")}'
    client.send(alias_message.encode('utf-8'))
    print(client.recv(1024).decode())

    thread = threading.Thread(target=handle_server, args=(client,))
    thread.start()

    while True:
        time.sleep(1)
        choice = input("FTP-Client>")

        while len(choice) == 0:
            choice = input("FTP-Client>")

        command_str = choice.split()
        opcode = get_OPCODE(command_str[0])
        client_send(client, opcode)

        if opcode != 'Command not supported':
            # print("Command is supported")

            if opcode == PUT_OPCODE or opcode == GET_OPCODE or opcode == CHANGE_OPCODE:
                if len(command_str) > 1:
                    fileNameLength = get_fileName_length(command_str[1])
                    print(opcode + " " + fileNameLength)
                    fileNameBinary = get_fileName_binary(command_str[1], fileNameLength)
                    print(fileNameBinary + " ")
                    print(get_string_from_binary(fileNameBinary))
                else:
                    print("\nCommand is not complete, please specify a file!\n")

            if opcode == HELP_OPCODE:
                client_send(client, choice)

        if choice == 'exit':
            print("Exit selected")
            client.close()
            sys.exit()


def client_send(client, message):
    client.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
