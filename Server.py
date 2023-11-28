import socket
from threading import Thread
import time
import sys

def main():

    while True:
        choice = input(
            "Possible commands: \n\n 'exit' to successfully kill server\n 'clear' to delete all registered users\n\n")

        if choice == 'exit':
            server.client_database.delete_database()
            time.sleep(1)
            sys.exit()

        if choice == 'clear':
            server.client_database.clear()
            server.client_database.delete_database()


if __name__ == '__main__':
    main()
