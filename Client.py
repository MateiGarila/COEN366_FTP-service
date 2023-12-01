import socket
import os
import sys
import threading
import time

PUT_OPCODE = '000'
GET_OPCODE = '001'
CHANGE_OPCODE = '010'
SUMMARY_OPCODE = '011'
HELP_OPCODE = '100'


# This method's purpose is to listen to the server's replies and to print them in the console
def handle_server(server):
    while True:
        message = server.recv(4096).decode()
        print(message)


# This method is dedicated to getting the opcode of the command
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


# This method returns the length of the file's name else it returns 'File name not supported'
def get_fileName_length(fileName):
    numChars = len(fileName)
    if numChars > 31:
        return 'File name not supported'
    else:
        binaryChars = bin(numChars)
        return binaryChars[2:].zfill(5)


# This method returns the name of the file in binary
def get_fileName_binary(fileName):
    binary_string = ''.join([bin(ord(c))[2:].zfill(8) for c in fileName])
    return binary_string


# This method returns the size of the specified file -- The file MUST be in the 'client_files' folder
def get_file_size(fileName):
    # REQUIRED 4 bytes for FS - 8 bits to a byte * 4
    numberOfBits = 8 * 4
    file_path = os.path.join('client_files', fileName)
    sizeOfFile = os.path.getsize(file_path)
    sizeOfFileBin = bin(sizeOfFile)[2:]
    return sizeOfFileBin.zfill(numberOfBits)


# This method takes a file's name and converts its contents to binary
def get_file_binary(fileName):
    file_path = os.path.join('client_files', fileName)
    with open(file_path, 'rb') as file:
        binary_data = ''.join(format(byte, '08b') for byte in file.read())

    return binary_data


# This method translates the binary sequence to its string equivalent
def get_string_from_binary(binaryStr):
    binary_bytes = bytearray(int(binaryStr[i:i + 8], 2) for i in range(0, len(binaryStr), 8))
    string = ""
    for byte in binary_bytes:
        if byte != 0:
            string += chr(byte)
    return string


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
        # The first 3 bits in the OPCODE byte
        opcode = get_OPCODE(command_str[0])
        # This is just to verify that commands do get through
        client_send(client, opcode)

        if opcode != 'Command not supported':
            if opcode == PUT_OPCODE or opcode == GET_OPCODE or opcode == CHANGE_OPCODE:
                # this makes sure that the client just doesn't type 'put'
                if len(command_str) > 1:
                    # the 5 bits in the OPCODE byte
                    fileNameLength = get_fileName_length(command_str[1])
                    print(opcode + " " + fileNameLength)
                    # this is the binary value of the file name in FL bytes
                    fileNameBinary = get_fileName_binary(command_str[1])
                    print(fileNameBinary)
                    # this is just a verification to make sure that the binary string corresponds to inputted file name
                    print(get_string_from_binary(fileNameBinary))
                    # this is the FS of the file to be transferred
                    sizeOfFile = get_file_size(command_str[1])
                    print(sizeOfFile)
                    file_data = get_file_binary(command_str[1])
                    print(file_data)
                    print(get_string_from_binary(file_data))
                else:
                    print("\nCommand is not complete, please specify a file!\n")

            if opcode == HELP_OPCODE:
                client_send(client, choice)

        if choice == 'exit':
            print("Exit selected")
            client.close()
            sys.exit()


# This method is used to send information to the server
def client_send(client, message):
    client.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
