import socket
import sys
import threading
import time

from client.Client_functions import handle_server_tcp, handle_server_udp, client_send_tcp, handle_put_request, \
    handle_get_request, handle_summary_request, handle_change_request, handle_help_request, client_send_udp
from ftp_functions.ftp_functions import (
    get_OPCODE
)
from ftp_constants import (
    PUT_OPCODE,
    GET_OPCODE,
    CHANGE_OPCODE,
    SUMMARY_OPCODE,
    HELP_OPCODE
)


def main(ip, port, protocol):
    if protocol == '1':
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_address = (ip, port)
        client_socket.connect((ip, port))
        print(f"Connected to {ip}:{port} using TCP")
        thread = threading.Thread(target=handle_server_tcp, args=(client_socket,))
        thread.start()

    elif protocol == '2':
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_address = (ip, port)
        print(f"Connected to {client_address} using UDP")
        client_send_udp(client_socket, 'Hello, Server!', client_address)
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
            handlers[opcode](client_socket, command_str, protocol, client_address)
        else:
            print('\nThis command is not supported! Please type "help" for a list of commands\n')
            if protocol == '1':
                client_send_tcp(client_socket, opcode)
            elif protocol == '2':
                client_send_udp(client_socket, opcode, client_address)

        if choice == 'bye':
            print("Exit selected")
            client_socket.close()
            thread.join()
            sys.exit()


if __name__ == '__main__':
    main()
