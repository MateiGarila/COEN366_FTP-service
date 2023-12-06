import socket
import sys
import threading
import time

from ftp_functions.ftp_functions import (
    put_command_builder,
    get_command_builder,
    get_string_from_binary,
    get_OPCODE,
    get_fileName_length,
    summary_command_builder,
    change_command_builder,
    get_decimal_from_binary,
    separate_bytes,
    create_file
)
from ftp_constants import (
    PUT_OPCODE,
    GET_OPCODE,
    CHANGE_OPCODE,
    SUMMARY_OPCODE,
    HELP_OPCODE,
    CORRECT_PUT_CHANGE,
    CORRECT_GET,
    STATISTICAL_SUMMARY,
    HELP_RESPONSE,
    FILE_SIZE_BYTES,
    CLIENT_FILES_DIRECTORY
)


def handle_get_response(response):
    # This part separates the remaining of the first byte (5 bits) to get the number of bytes for the file name
    fileNameLength = response[:5]
    response = response[5:]
    fileNameLength = get_decimal_from_binary(fileNameLength)

    # This part separates the CORRECT number of bytes reserved for the file name and saves it in 'fileName'
    fileName, response = separate_bytes(response, fileNameLength)

    # This part separates 4 bytes which are reserved for the File Size (FS) and saves it in 'fileSize'
    fileSize, response = separate_bytes(response, FILE_SIZE_BYTES)
    fileSize = get_decimal_from_binary(fileSize)

    # This part separates the remaining bytes reserved for the file data - normally the remaining bytes are all about
    # the file data - be thorough - the file data is saved in 'fileData' - request should technically be an empty string
    fileData, response = separate_bytes(response, fileSize)

    create_file(CLIENT_FILES_DIRECTORY, get_string_from_binary(fileName), get_string_from_binary(fileData))


# This method's purpose is to listen to the server's replies and to print them in the console
def handle_server(server):
    while True:
        # This is the messages the server sends the client
        message = server.recv(4096).decode()
        # print("Server reply: " + message)
        # Need better handling
        opcode = message[:3]
        message = message[3:]

        # From here redirect to corresponding request handler
        if opcode == CORRECT_PUT_CHANGE:
            print('\nFile successfully updated!\n')
        elif opcode == CORRECT_GET:
            print("\nFile successfully fetched\n")
            handle_get_response(message)
        elif opcode == STATISTICAL_SUMMARY:
            print("\nFile successfully fetched statistical summary!\n")
        elif opcode == HELP_RESPONSE:
            remaining_byte = message[:5]
            message = message[5:]
            messageLength = get_decimal_from_binary(remaining_byte)
            response, message = separate_bytes(message, messageLength)
            print("\n" + get_string_from_binary(response) + "\n")


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

        while len(choice) < 3:
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
                            # print("Put request: " + put_request)
                            client_send(client, put_request)
                        else:
                            print("\nThe name of the file exceeds 31 characters, please refactor the file's name\n")
                    elif opcode == GET_OPCODE:

                        if len(command_str[1]) <= 31:
                            get_request = get_command_builder(command_str)
                            get_request = opcode + get_request
                            # print("Get request: " + get_request)
                            client_send(client, get_request)
                        else:
                            print("\nThe name of the file exceeds 31 characters, please refactor the file's name\n")

                    elif opcode == SUMMARY_OPCODE:
                        if len(command_str[1]) <= 31:
                            summary_request = opcode + summary_command_builder(command_str)
                            # print("Summary request: " + summary_request)
                            client_send(client, summary_request)
                        else:
                            print("\nThe name of the file exceeds 31 characters, please refactor the file's name\n")

                    elif opcode == CHANGE_OPCODE:
                        if len(command_str) > 1:
                            # print(command_str)
                            if len(command_str[1]) <= 31:
                                # print(command_str[1])
                                change_request_old = change_command_builder(command_str)
                                print("Change request: " + change_request_old)
                                if len(command_str) > 2:
                                    if len(command_str[2]) <= 31:
                                        # print(command_str[2])
                                        change_request_new = change_command_builder([command_str[0], command_str[2]])
                                        change_request_new = opcode + change_request_old + change_request_new
                                        print("Complete change request: " + change_request_new)
                                        client_send(client, change_request_new)
                                    else:
                                        print(
                                            "\nThe name of the second file exceeds 31 characters, please refactor the "
                                            "file's name\n")
                                else:
                                    print("\nCommand is not complete, please specify a second file!\n")
                            else:
                                print(
                                    "\nThe name of the first file exceeds 31 characters, please refactor the file's "
                                    "name\n")
                        else:
                            print("\nCommand is not complete, please specify a file!\n")

            if opcode == HELP_OPCODE:
                help_request = opcode + get_fileName_length("")
                client_send(client, help_request)

        else:
            print('\nThis command is not supported! Please type "help" for a list of commands\n')

        if choice == 'bye':
            print("Exit selected")
            client.close()
            sys.exit()


# This method is used to send information to the server
def client_send(client, message):
    client.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
