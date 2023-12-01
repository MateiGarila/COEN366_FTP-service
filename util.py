import os


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
    file_path = os.path.join('client_files', fileName)
    sizeOfFile = os.path.getsize(file_path)
    sizeOfFileBin = bin(sizeOfFile)[2:]
    return sizeOfFileBin.zfill(numberOfBits)


# This method takes a file's name and converts its contents to binary
def get_file_binary_client(fileName):
    file_path = os.path.join('client_files', fileName)
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
