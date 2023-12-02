import socket
import sys
import threading
import time

from ftp_functions.ftp_functions import (
    put_command_builder,
    get_string_from_binary,
    get_OPCODE,
    get_fileName_length,
    summary_command_builder,
    change_file_name
)
from ftp_constants import (
    PUT_OPCODE,
    GET_OPCODE,
    CHANGE_OPCODE,
    SUMMARY_OPCODE,
    HELP_OPCODE,
    HELP_RESPONSE
)


# This method's purpose is to listen to the server's replies and to print them in the console
def handle_server(server):
    while True:
        message = server.recv(4096).decode()
        test = message[8:]
        print(get_string_from_binary(test))


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
                    elif opcode == SUMMARY_OPCODE:
                        summary_request = opcode + summary_command_builder(command_str)
                        # print(summary_request)
                        client_send(client, summary_request)
                    elif opcode == CHANGE_OPCODE:
                        change_request = opcode + change_file_name(command_str)
                        client_send(client, change_request)

                else:
                    print("\nCommand is not complete, please specify a file!\n")

            if opcode == HELP_OPCODE:
                help_request = opcode + get_fileName_length("")
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
