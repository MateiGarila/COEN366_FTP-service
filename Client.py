import socket
import os
import sys


def main():
    s = socket.socket()
    port = 12000
    s.connect(('127.0.0.1', port))

    commandList = ("'put' to UPLOAD a file\n 'get' to DOWNLOAD a file\n 'summary' to get the maximum, minimum and "
                   "average of the numbers of the specified file\n 'change' to UPDATE the name of a specified file\n "
                   "'help' to receive a list of commands \n 'exit' to break connection with server")
    print(s.recv(1024))

    while True:
        choice = input("Possible commands: \n\n" + commandList + "\n\nFTP-Client>")

        if choice == 'put':
            print("put selected")

        if choice == 'get':
            print("get selected")

        if choice == 'summary':
            print("summary selected")

        if choice == 'change':
            print("change selected")

        if choice == 'help':
            print(commandList)

        if choice == 'exit':
            print("Exit selected")
            s.close()
            sys.exit()

    s.close()


if __name__ == '__main__':
    main()
