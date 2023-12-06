import os
from ftp_constants import (
    SERVER_FILES_DIRECTORY,
    CLIENT_FILES_DIRECTORY,
    FILE_SIZE_BYTES,
    SUMMARY_OPCODE,
    PUT_OPCODE,
    GET_OPCODE,
    CHANGE_OPCODE,
    HELP_OPCODE
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


# This method returns the file path for files in the 'client_files' directory
def get_file_path(directory, fileName):
    file_path = os.path.join(directory, fileName)
    return file_path


# This method returns the length of the file's name
def get_fileName_length(fileName):
    numChars = len(fileName)
    if numChars == 0:
        return '00000'
    else:
        binaryChars = bin(numChars)
        return binaryChars[2:].zfill(5)


# This method receives a binary string and returns the contents as an integer -- no handling for binary string longer
# than integer i.e. if you give it a word instead of a number it's probably, definitely going to crash
def get_decimal_from_binary(binaryStr):
    return int(binaryStr, 2)


# This method returns the string in binary form
def get_binary_string(string):
    binary_string = ''.join([bin(ord(c))[2:].zfill(8) for c in string])
    return binary_string


# This method returns the size of the specified file
def get_file_size(directory, fileName):
    # REQUIRED 4 bytes for FS - 8 bits to a byte * 4
    numberOfBits = 8 * FILE_SIZE_BYTES
    file_path = get_file_path(directory, fileName)
    sizeOfFile = os.path.getsize(file_path)
    sizeOfFileBin = bin(sizeOfFile)[2:]
    return sizeOfFileBin.zfill(numberOfBits)


# This method takes a file's name and converts its contents to binary
def get_file_binary(directory, fileName):
    file_path = get_file_path(directory, fileName)
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


# This method writes file to the specified 'directory', with the corresponding 'fileName' and 'fileData'
def create_file(directory, fileName, fileData):
    if not os.path.exists(directory):
        os.makedirs(directory)

    full_path = os.path.join(directory, fileName)

    with open(full_path, 'w') as file:
        file.write(fileData)


# This method creates the put request which will be sent to the server
def put_command_builder(command_str):
    # the 5 bits in the OPCODE byte (FL)
    fileNameLength = get_fileName_length(command_str[1])
    # print("File name length " + fileNameLength)
    # this is the binary value of the file name in FL bytes
    fileNameBinary = get_binary_string(command_str[1])
    # print("File name in binary: " + fileNameBinary)
    # this is just a verification to make sure that the binary string corresponds to inputted file name
    # print(get_string_from_binary(fileNameBinary))
    # this is the FS of the file to be transferred
    sizeOfFile = get_file_size(CLIENT_FILES_DIRECTORY, command_str[1])
    # print("Size of file: " + sizeOfFile)
    file_data = get_file_binary(CLIENT_FILES_DIRECTORY, command_str[1])
    # print("File data: " + file_data)
    # print(get_string_from_binary(file_data))
    return fileNameLength + fileNameBinary + sizeOfFile + file_data


# This method creates the get request which will be sent to the server
def get_command_builder(command_str):
    # the 5 bits un the OPCODE byte (FL)
    fileNameLength = get_fileName_length(command_str[1])
    # 'fileNameBinary' consists of FL bytes
    fileNameBinary = get_binary_string(command_str[1])
    return fileNameLength + fileNameBinary


def summary_command_builder(command_str):
    # the 5 bits in the OPCODE byte (FL)
    fileNameLength = get_fileName_length(command_str[1])
    # print("File name length " + fileNameLength)
    # this is the binary value of the file name in FL bytes
    fileNameBinary = get_binary_string(command_str[1])
    # print("File name in binary: " + fileNameBinary)
    # this is just a verification to make sure that the binary string corresponds to inputted file name
    # print(get_string_from_binary(fileNameBinary))
    file_data = get_file_binary(SERVER_FILES_DIRECTORY, command_str[1])
    # print("File data: " + file_data)
    # print(get_string_from_binary(file_data))
    return fileNameLength + fileNameBinary + file_data


def change_command_builder(command_str):
    # the 5 bits in the OPCODE byte (FL)
    fileNameLength = get_fileName_length(command_str[1])
    print("File name length " + fileNameLength)
    # this is the binary value of the file name in FL bytes
    fileNameBinary = get_binary_string(command_str[1])
    print("File name in binary: " + fileNameBinary)
    print(get_string_from_binary(fileNameBinary))
    return fileNameLength + fileNameBinary


def change_file_name(fileName, newName):
    # Extract the file name from the command
    file_path_old = get_file_path(SERVER_FILES_DIRECTORY, fileName)
    file_path_New = os.path.join(SERVER_FILES_DIRECTORY, newName)
    os.rename(file_path_old, file_path_New)


# Given a binary string this method will separate the corresponding number of bytes and return the separated string and
# the remaining binary string
def separate_bytes(binary_string, num_bytes):
    # Calculate the number of bytes to process
    actual_num_bytes = len(binary_string) // 8

    # Print the values for debugging
    # print("actual_num_bytes:", actual_num_bytes)
    # print("num_bytes:", num_bytes)

    # Ensure the input number of bytes is within a valid range
    if not (0 <= num_bytes <= actual_num_bytes):
        raise ValueError("The input number of bytes is not within a valid range.")

    # Process each byte
    byte_values = []
    for i in range(actual_num_bytes):
        start = i * 8
        end = start + 8
        byte_string = binary_string[start:end]
        byte_value = format(int(byte_string, 2), '08b')
        byte_values.append(byte_value)

    # Calculate the number of remaining bits dynamically
    remaining_bits = len(binary_string) % 8

    # Handle remaining bits
    if remaining_bits > 0:
        last_byte_string = binary_string[-remaining_bits:].ljust(8, '0')
        last_byte_value = format(int(last_byte_string, 2), '08b')
        byte_values.append(last_byte_value)

    # Separate the specified number of bytes and the remaining bytes
    separated_bytes = byte_values[:num_bytes]
    remaining_bytes = byte_values[num_bytes:]

    # Convert the byte values to strings
    separated_bytes_str = ''.join(separated_bytes)
    remaining_bytes_str = ''.join(remaining_bytes)

    # Print the separated and remaining bytes for debugging
    # print("separated_bytes_str:", separated_bytes_str)
    # print("remaining_bytes_str:", remaining_bytes_str)

    return separated_bytes_str, remaining_bytes_str


# This method searches the specified 'directory' for the specified 'file_name'
def search_file(directory, file_name):
    if not os.path.exists(directory):
        return "Directory does not exist"
    else:
        for root, dirs, files in os.walk(directory):
            if file_name in files:
                return True
        return False
