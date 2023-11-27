import socket
from threading import Thread
import time
import sys
from Util.UtilityFunctions import get_ip_address
from ClientDatabase import Database


class Server(Thread):
    # fixed UDP port and buffer size
    UDP_PORT = 5001
    BUFFER_SIZE = 4096

    def __init__(self):
        super.__init__()
        self.client_database = Database()
        self.client_list = self.client_database.open_database()
        self.ip_address = get_ip_address()
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind((self.ip_address, self.UDP_PORT))
        print("Server Listening: " + str(self.udp_socket))

    # Still need to code the "def run(self)" function

def main():
    server = Server()
    server.daemon = True
    server.start()

    while True:
        choice = input(
            "Possible commands: \n\n 'exit' to successfully kill server\n 'clear' to delete all registered users\n\n")

        if choice == 'exit':
            time.sleep(1)
            sys.exit()

        if choice == 'clear':
            print("clear selected")
            # clear client list
            # clear database


if __name__ == '__main__':
    main()
