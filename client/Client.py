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
    create_file, validate_filename_length
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
    CLIENT_FILES_DIRECTORY,
    EMPTY_FIRST_BITS
)


def send_request(client, opcode, request_builder):
    request = opcode + request_builder
    # print(f"{opcode.capitalize()} request: {request}")
    client_send(client, request)


def send_request_udp(client, opcode, request_builder, client_address):
    request = opcode + request_builder
    # print(f"{opcode.capitalize()} request: {request}")
    client_send(client, request, client_address)


def handle_put_request(client, command_str):
    if validate_filename_length(command_str[1]):
        send_request(client, PUT_OPCODE, put_command_builder(command_str))


def handle_get_request(client, command_str):
    if validate_filename_length(command_str[1]):
        send_request(client, GET_OPCODE, get_command_builder(command_str))


def handle_summary_request(client, command_str):
    if validate_filename_length(command_str[1]):
        send_request(client, SUMMARY_OPCODE, summary_command_builder(command_str))


def handle_change_request(client, command_str):
    if len(command_str) > 1 and validate_filename_length(command_str[1]):
        change_request_old = change_command_builder(command_str)
        # print(f"Change request: {change_request_old}")

        if len(command_str) > 2 and validate_filename_length(command_str[2]):
            change_request_new = change_command_builder([command_str[0], command_str[2]])
            send_request(client, CHANGE_OPCODE, change_request_old + change_request_new)
        else:
            print("\nCommand is not complete, please specify a second file!\n")
    else:
        print("\nCommand is not complete, please specify a file!\n")


def handle_help_request(client):
    send_request(client, EMPTY_FIRST_BITS, HELP_OPCODE)


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
def handle_server_tcp(client_socket):
    while True:
        # This is the messages the server sends the client
        message = client_socket.recv(4096).decode()
        print("Server reply: " + message)
        # Need better handling
        opcode = message[:3]
        message = message[3:]

        print(opcode)

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
        else:
            print("Unknown opcode:", opcode)


def handle_server_udp(client_socket):
    # This is the messages the server sends the client
    data, server_address = client_socket.recvfrom(1024)
    message = data.decode('utf-8')
    print(f"Received response from server {message}")

    # Need better handling
    opcode = message[:3]
    message = message[3:]

    print(opcode)

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
    else:
        print("Unknown opcode:", opcode)


def main(ip, port, protocol):
    if protocol == '1':
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print(f"Connected to {ip}:{port} using TCP")
        thread = threading.Thread(target=handle_server_tcp, args=(client_socket,))
        thread.start()

    elif protocol == '2':
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (ip, port)
        print(f"Connected to {server_address} using UDP")
        thread = threading.Thread(target=handle_server_udp, args=(client_socket,))
        thread.start()

    while True:
        time.sleep(1)
        choice = input("FTP-Client>")

        while len(choice) < 3:
            choice = input("FTP-Client>")

        command_str = choice.split()
        # The first 3 bits in the OPCODE byte
        opcode = get_OPCODE(command_str[0])

        if opcode in {PUT_OPCODE, GET_OPCODE, SUMMARY_OPCODE, CHANGE_OPCODE, HELP_OPCODE}:
            handlers = {
                PUT_OPCODE: handle_put_request,
                GET_OPCODE: handle_get_request,
                SUMMARY_OPCODE: handle_summary_request,
                CHANGE_OPCODE: handle_change_request,
                HELP_OPCODE: handle_help_request,
            }
            handlers[opcode](client_socket, command_str)
        else:
            print('\nThis command is not supported! Please type "help" for a list of commands\n')
            client_send(client_socket, opcode)

        if choice == 'bye':
            print("Exit selected")
            client_socket.close()
            thread.join()
            sys.exit()


def client_send(client, message):
    client.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
