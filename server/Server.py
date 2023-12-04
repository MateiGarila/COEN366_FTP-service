import socket
import string
import threading

from ftp_functions.ftp_functions import (
    get_binary_string,
    get_decimal_from_binary,
    separate_bytes,
    get_string_from_binary,
    create_file,
    search_file,
    get_file_size,
    get_file_binary
)
from ftp_constants import (
    PUT_OPCODE,
    GET_OPCODE,
    CHANGE_OPCODE,
    SUMMARY_OPCODE,
    HELP_OPCODE,
    HELP_RESPONSE,
    FILE_SIZE_BYTES,
    SERVER_FILES_DIRECTORY,
    ERROR_FILE_NOT_FOUND,
    EMPTY_FIRST_BITS,
    CORRECT_GET
)

clients = []
aliases = []


# This method handles the 'help' request
def handle_request_help():
    # commandList the way it is now is exactly 31 bytes long. Which is the maximum allowed to be transferred to the user
    commandList = "bye change get help put summary"
    commandInBits = get_binary_string(commandList)
    commandBytes = len(commandInBits) // 8
    bytesInBits = bin(commandBytes)[2:].zfill(5)
    return HELP_RESPONSE + bytesInBits + commandInBits


# This method handles the 'put' request
def handle_put_request(request):
    # This part separates the remaining of the first byte (5 bits) to get the number of bytes for the file name
    fileNameLength = request[:5]
    request = request[5:]
    fileNameLength = get_decimal_from_binary(fileNameLength)

    # This part separates the CORRECT number of bytes reserved for the file name and saves it in 'fileName'
    fileName, request = separate_bytes(request, fileNameLength)

    # This part separates 4 bytes which are reserved for the File Size (FS) and saves it in 'fileSize'
    fileSize, request = separate_bytes(request, FILE_SIZE_BYTES)
    fileSize = get_decimal_from_binary(fileSize)

    # This part separates the remaining bytes reserved for the file data - normally the remaining bytes are all about
    # the file data - be thorough - the file data is saved in 'fileData' - request should technically be an empty string
    fileData, request = separate_bytes(request, fileSize)

    create_file(SERVER_FILES_DIRECTORY, get_string_from_binary(fileName), get_string_from_binary(fileData))

    return '00000000'


def handle_get_request(request):
    fileNameLengthBin = request[:5]
    request = request[5:]

    fileNameLength = get_decimal_from_binary(fileNameLengthBin)

    fileNameBin, request = separate_bytes(request, fileNameLength)
    fileName = get_string_from_binary(fileNameBin)
    if not search_file(SERVER_FILES_DIRECTORY, fileName):
        return ERROR_FILE_NOT_FOUND + EMPTY_FIRST_BITS
    else:
        # At this point we have Res-code, filename length and filename all we need is file size and file data
        sizeOfFile = get_file_size(SERVER_FILES_DIRECTORY, fileName)
        fileData = get_file_binary(SERVER_FILES_DIRECTORY, fileName)
        return CORRECT_GET + fileNameLengthBin + fileNameBin + sizeOfFile + fileData


# The purpose of this function is to listen to the client's requests and to reply to the client
def handle_client(client):
    while True:
        # this 'message' is what the client sent to the server
        message = client.recv(4096).decode()
        # print("Message received by server: " + message)
        opcode = message[:3]
        fileLength = message[3:8]
        message = message[3:]
        # print("Opcode: " + opcode)
        # print("File Length: " + fileLength)
        # print("Message: " + message)

        # From here redirect to corresponding request handler
        if opcode == PUT_OPCODE:
            put_response = handle_put_request(message)
            server_send(client, put_response)
        elif opcode == GET_OPCODE:
            get_response = handle_get_request(message)
            # print("Server sending: " + get_response)
            server_send(client, get_response)
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
