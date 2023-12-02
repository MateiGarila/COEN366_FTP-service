import os
from ftp_constants import (
    PUT_OPCODE,
    GET_OPCODE,
    CHANGE_OPCODE,
    SUMMARY_OPCODE,
    HELP_OPCODE,
    HELP_RESPONSE
)


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


def getFilePath(fileName):
    file_path = os.path.join('client_files', fileName)
    return file_path


# This method returns the length of the file's name else it returns 'File name not supported'
def get_fileName_length(fileName):
    numChars = len(fileName)
    if numChars == 0:
        return '00000'
    else:
        binaryChars = bin(numChars)
        return binaryChars[2:].zfill(5)


# This method returns the string in binary form
def get_binary_string(string):
    binary_string = ''.join([bin(ord(c))[2:].zfill(8) for c in string])
    return binary_string


# This method returns the size of the specified file -- The file MUST be in the 'client_files' folder
def get_file_size(fileName):
    # REQUIRED 4 bytes for FS - 8 bits to a byte * 4
    numberOfBits = 8 * 4
    file_path = getFilePath(fileName)
    sizeOfFile = os.path.getsize(file_path)
    sizeOfFileBin = bin(sizeOfFile)[2:]
    return sizeOfFileBin.zfill(numberOfBits)


# This method takes a file's name and converts its contents to binary
def get_file_binary_client(fileName):
    file_path = getFilePath(fileName)
    with open(file_path, 'rb') as file:
        binary_data = ''.join(format(byte, '08b') for byte in file.read())

    return binary_data


# This method translates the binary sequence to its string equivalent
def get_string_from_binary(binaryStr):
    binary_bytes = bytearray(int(binaryStr[i:i + 8], 2) for i in range(0, len(binaryStr), 8))
    string = ""
    for byte in binary_bytes:
        if byte != 0:
            string += chr(byte)
    return string


def put_command_builder(command_str):
    # the 5 bits in the OPCODE byte (FL)
    fileNameLength = get_fileName_length(command_str[1])
    print("File name length " + fileNameLength)
    # this is the binary value of the file name in FL bytes
    fileNameBinary = get_binary_string(command_str[1])
    print("File name in binary: " + fileNameBinary)
    # this is just a verification to make sure that the binary string corresponds to inputted file name
    print(get_string_from_binary(fileNameBinary))
    # this is the FS of the file to be transferred
    sizeOfFile = get_file_size(command_str[1])
    print("Size of file: " + sizeOfFile)
    file_data = get_file_binary_client(command_str[1])
    print("File data: " + file_data)
    print(get_string_from_binary(file_data))
    return fileNameLength + fileNameBinary + sizeOfFile + file_data


def summary_command_builder(command_str):
    # Extract the file name from the command
    file_name = command_str[1]
    file_path = getFilePath(file_name)
    if not os.path.exists(file_path):
        return f"File '{file_name}' does not exist."

    with open(file_path, 'r') as file:
        numbers = file.read()

    numbers = [float(num) for num in numbers.split()]

    max_value = max(numbers)
    min_value = min(numbers)
    avg_value = sum(numbers) / len(numbers)

    # Create the summary response
    summary_response = f"Summary for {file_name}:\nMaximum: {max_value}\nMinimum: {min_value}\nAverage: {avg_value}"

    summary_file_path = os.path.join('client_files', 'summary.txt')
    with open(summary_file_path, 'w') as summary:
        summary.write(summary_response)

    return summary_response


def change_file_name(command_str):
    # Extract the file name from the command
    file_name = command_str[1]
    file_path_old = getFilePath(file_name)
    if not os.path.exists(file_path_old):
        return f"File '{file_name}' does not exist."

    newName = input("Enter new name of file: ")
    file_path_New = os.path.join('client_files', newName)

    os.rename(file_path_old, file_path_New)

    return newName
