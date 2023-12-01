import socket
import sys
import threading
import time
import util

PUT_OPCODE = '000'
GET_OPCODE = '001'
CHANGE_OPCODE = '010'
SUMMARY_OPCODE = '011'
HELP_OPCODE = '100'


# This method's purpose is to listen to the server's replies and to print them in the console
def handle_server(server):
    while True:
        message = server.recv(4096).decode()
        test = message[8:]
        print(util.get_string_from_binary(test))


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


def put_command_builder(command_str):
    # the 5 bits in the OPCODE byte (FL)
    fileNameLength = util.get_fileName_length(command_str[1])
    print("File name length " + fileNameLength)
    # this is the binary value of the file name in FL bytes
    fileNameBinary = util.get_binary_string(command_str[1])
    print("File name in binary: " + fileNameBinary)
    # this is just a verification to make sure that the binary string corresponds to inputted file name
    print(util.get_string_from_binary(fileNameBinary))
    # this is the FS of the file to be transferred
    sizeOfFile = util.get_file_size(command_str[1])
    print("Size of file: " + sizeOfFile)
    file_data = util.get_file_binary_client(command_str[1])
    print("File data: " + file_data)
    print(util.get_string_from_binary(file_data))
    return fileNameLength + fileNameBinary + sizeOfFile + file_data


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

        if opcode != 'Command not supported':
            if opcode == PUT_OPCODE or opcode == GET_OPCODE or opcode == CHANGE_OPCODE or opcode == SUMMARY_OPCODE:
                if len(command_str) > 1:
                    if opcode == PUT_OPCODE:
                        if len(command_str[1]) <= 31:
                            put_request = put_command_builder(command_str)
                            put_request = opcode + put_request
                            print(put_request)
                            client_send(client, put_request)
                        else:
                            print("\nThe name of the file exceeds 31 characters, please refactor the file's name\n")
                else:
                    print("\nCommand is not complete, please specify a file!\n")

            if opcode == HELP_OPCODE:
                help_request = opcode + util.get_fileName_length("")
                client_send(client, help_request)

        if choice == 'exit':
            print("Exit selected")
            client.close()
            sys.exit()


# This method is used to send information to the server
def client_send(client, message):
    client.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
