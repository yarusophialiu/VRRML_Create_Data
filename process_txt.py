# # Path to your text file
# bitrates = [4000]

# for bitrate in bitrates:
#     file_path = f"./04-21/{bitrate}bps.txt"

#     # Read the file and filter out lines
#     with open(file_path, "r") as file:
#         lines = file.readlines()
#     # filtered_lines = [line for line in lines if not line.strip().lower().startswith("no change")]

#     # filtered_lines = [line for line in lines if not line.strip().lower().startswith(('output_dir', 'fps_dir', 'ref_dir', 'Command'))]
#     filtered_lines = [line for line in lines if line.strip()]


#     # Write the filtered lines back to the file
#     with open(file_path, "w") as file:
#         file.writelines(filtered_lines)
import re
import codecs


def process_file(input_file, output_cvvdp, output_details):
    open(output_cvvdp, 'w').close()
    open(output_details, 'w').close()

    cvvdp_pattern = re.compile(r'^cvvdp=\d+\.\d+ \[\w+\]$')  # Matches 'cvvdp=8.2407 [JOD]'
    details_pattern = re.compile(r'^\w+\.png \d+\.\d+ \d+ \d+$')  # Matches '0e7ac87fac42cece_test_10_90_360_16000.png 90.0 360 16000'


    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
            print(f'\n\n\line {line}')
            line = line.strip()
            print(f'line {line} {type(line)}')
            print("cvvdp=" in str(line))
            print("png" in line)

    
    # with open(output_cvvdp, 'w') as cvvdp_file, open(output_details, 'w') as details_file:
    #      for line in lines:
    #         print(f'\n\n\line {line}')
    #         line = line.strip()
    #         print(f'line {line} {type(line)}')
    #         print("cvvdp=" in str(line))
    #         print(line.find("cvvdp"))
    #         print(line.find("png"))
    #         if 'cvvdp=' in line:
    #             print(f'cvvdp')
    #             # cvvdp_file.write(line + '\n')
    #         elif '.png' in line and line.count(' ') == 4:
    #             print(f'details_pattern')

                # details_file.write(line + '\n')



def remove_lines_with_string(file_path, substring):
    # Open the file and read lines
    with open(file_path, 'r', encoding='utf-16') as file:
        lines = file.readlines()
    # print(f'lines {lines}')
    # Filter out lines containing the substring '4000.png'
    lines_to_keep = [line for line in lines if substring in line]
    print(f'lines_to_keep \n {lines_to_keep}')

    with open(file_path, 'w', encoding='utf-16') as file:
        file.writelines(lines_to_keep)
    print(f"Lines containing '{substring}' have been removed from {file_path}.")

# Specify the path to your file
file_path = '04-22/11-58/4000bps copy.txt'

# Call the function to remove lines containing '4000.png'
remove_lines_with_string(file_path, '4000.png')


# Define the file paths
# input_file = '04-22/11-58/4000bps.txt'
# output_cvvdp = '04-22/16000_2bps_cvvdp_values.txt'
# output_details = '04-22/16000_2bps_files.txt'

# # Call the function with file paths
# process_file(input_file, output_cvvdp, output_details)

# def check():
#     s = "cvvdp=9.1939 [JOD]"
#     s = s.strip()
#     print("cvvdp=" in s)

# check()
