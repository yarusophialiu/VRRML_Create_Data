
import base64
import struct
import chardet


base_path = f'C:/Users/15142/new/Falcor/Source/Samples/EncodeDecode/'
binary_file_path = f'{base_path}/motion_30_720_5000.txt'

# with open(binary_file_path, 'r') as text_file:
#     # Read the hexadecimal string from the text file
#     hex_data = text_file.read()

# # Convert the hexadecimal string back to binary data
# binary_data = bytes.fromhex(hex_data)
# # binary_data = base64.b64decode(base64_encoded_data)
with open(binary_file_path, mode='rb') as file: # b is important -> binary
    binary_data = file.read()

# Print the binary data
encoding = 'utf-8'
print(binary_data.decode(encoding='latin-1'))
