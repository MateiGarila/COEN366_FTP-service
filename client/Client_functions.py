from ftp_constants import (
    SERVER_FILES_DIRECTORY,
    FILE_SIZE_BYTES,
    SUMMARY_OPCODE,
    HELP_RESPONSE,
    PUT_OPCODE,
    EMPTY_FIRST_BITS,
    STATISTICAL_SUMMARY,
    GET_OPCODE,
    ERROR_FILE_NOT_FOUND,
    CHANGE_OPCODE,
    CORRECT_GET,
    HELP_OPCODE, UNSUCCESSFUL_CHANGE, CORRECT_PUT_CHANGE, ERROR_UNKNOWN_REQUEST, CLIENT_FILES_DIRECTORY
)

from ftp_functions.ftp_functions import (
    get_binary_string,
    get_decimal_from_binary,
    separate_bytes,
    get_string_from_binary,
    create_file,
    search_file,
    get_file_size,
    get_file_binary,
    change_file_name,
    process_file_data, validate_filename_length, put_command_builder, get_command_builder, summary_command_builder,
    change_command_builder
)


def send_request_tcp(client, opcode, request_builder):
    request = opcode + request_builder
    # print(f"{opcode.capitalize()} request: {request}")
    client_send(client, request)


def send_request_udp(client, opcode, request_builder, client_address):
    request = opcode + request_builder
    # print(f"{opcode.capitalize()} request: {request}")
    client_send_udp(client, request, client_address)


def handle_put_request(client, command_str, protocol, server_address):
    if validate_filename_length(command_str[1]):
        if protocol == '1':
            send_request_tcp(client, PUT_OPCODE, put_command_builder(command_str))
        elif protocol == '2':
            send_request_udp(client, PUT_OPCODE, put_command_builder(command_str), server_address)


def handle_get_request(client, command_str, protocol, server_address):
    if validate_filename_length(command_str[1]):
        if protocol == '1':
            send_request_tcp(client, GET_OPCODE, get_command_builder(command_str))
        elif protocol == '2':
            send_request_udp(client, GET_OPCODE, get_command_builder(command_str), server_address)


def handle_summary_request(client, command_str, protocol, server_address):
    if validate_filename_length(command_str[1]):
        if protocol == '1':
            send_request_tcp(client, SUMMARY_OPCODE, summary_command_builder(command_str))
        elif protocol == '2':
            send_request_udp(client, SUMMARY_OPCODE, summary_command_builder(command_str), server_address)


def handle_change_request(client, command_str, protocol, server_address):
    if len(command_str) > 1 and validate_filename_length(command_str[1]):
        change_request_old = change_command_builder(command_str)

        if len(command_str) > 2 and validate_filename_length(command_str[2]):
            change_request_new = change_command_builder([command_str[0], command_str[2]])
            if protocol == '1':
                send_request_tcp(client, CHANGE_OPCODE, change_request_old + change_request_new)
            elif protocol == '2':
                send_request_udp(client, CHANGE_OPCODE, change_request_old + change_request_new, server_address)
        else:
            print("\nCommand is not complete, please specify a second file!\n")
    else:
        print("\nCommand is not complete, please specify a file!\n")


def handle_help_request(client, protocol, server_address):
    if protocol == '1':
        send_request_tcp(client, EMPTY_FIRST_BITS, HELP_OPCODE)
    elif protocol == '2':
        send_request_udp(client, EMPTY_FIRST_BITS, HELP_OPCODE, server_address)


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


def client_send(server_socket, message):
    server_socket.send(message.encode('utf-8'))


def handle_server_udp(client_socket):
    while True:
        # This is the messages the server sends the client
        data, server_address = client_socket.recvfrom(1024)
        message = data.decode()
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


def client_send_udp(server_socket, message, client_address):
    # print(server_socket, message, client_address)
    server_socket.sendto(message.encode(), client_address)
