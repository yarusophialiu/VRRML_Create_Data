import os
from utils import *

def count_files_in_subfolders(root_directory):
    # Traverse the directory tree starting from the root directory
    print(f'root directory {root_directory}')
    count = 0
    count_dir = 0
    for root, dirs, files in os.walk(root_directory):
        dirs.sort()
#        print(f'Sorted dirs: {dirs}')
        for dir_name in dirs:
            subfolder_path = os.path.join(root, dir_name)
            print(f'\ndir_name {dir_name}')
            count_dir += 1
            os.chdir(subfolder_path)
            current_directory = os.getcwd()

            print(os.listdir(current_directory))
            for bitrate in os.listdir(current_directory):
                bitrate_path = os.path.join(subfolder_path, bitrate)
                files_num = len(os.listdir(bitrate_path))
                # print(f'bitrate {bitrate}, files_num {files_num}')
                count += files_num
            os.chdir('../../')
            current_directory = os.getcwd()
            # print(f"Current working directory: {current_directory}")
#            break
        break
    print(f'count_dir {count_dir}, count {count}')



def count_files_in_folders(root_directory):
    # Traverse the directory tree starting from the root directory
    count = 0
    count_dir = 0
    for root in os.listdir(root_directory):
        root_path = os.path.join(root_directory, root)
        # print(f'root {root}')
        file_count = len(os.listdir(root_path))
        print(f'root {file_count} {root}')
        count += file_count
        count_dir += 1
    print(f'count_dir {count_dir}, count {count}')




if __name__ == '__main__':
    # scene_arr = ["crytek_sponza", "room"] # crytek_sponza, sibenik, room, bedroom
    scene_arr = ["bistro"] # crytek_sponza, sibenik, room, bedroom
    base_directory = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\HPC\cleaned_patches'
    base_directory = r'C:\Users\15142\Projects\VRR\Data\VRRML\ML\train\bedroom_path1_seg1_1' # train folder 1440000, train_bitratelabel 288000, test, val 28800
    base_directory = r'C:\Users\15142\Projects\VRR\Data\VRRML\ML\train_bitratelabel' # train folder 1440000, train_bitratelabel 288000, test, val 28800
    base_directory = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\2024-09-19\reference'
    base_directory = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\reference' # train 402435 val 49668 test 44697, 128x128 test 35756
    base_directory = r'C:\Users\15142\Projects\VRR\Data\VRRML\ML\reference128X128' 
    # train 402435 val 49668 test 44697, 128x128 test 35756
    # under train, 20 patches per video, under train_bitratelabel, 4 patches a video
    for scene in scene_arr:
        root_directory = f'{base_directory}/validation'
        print(f'\n\n\nroot dir {root_directory}')
        # count_files_in_subfolders(root_directory)
        count_files_in_folders(root_directory)

#    root_directory = r'/home/yl962/rds/hpc-work/VRR/Data/VRR_Patches/2024-09-12/crytek_sponza'
#    print(f'root dir {root_directory}')

# if __name__ == '__main__':
#     # scene_arr = ["suntemple", "sibenik"] # crytek_sponza, sibenik, room, bedroom
#     # for scene in scene_arr:
#     # root_directory = f'/home/yl962/rds/hpc-work/VRR/Data/VRR_Patches/2024-09-12/{scene}'
#     root_directory = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\HPC\2024-09-12\bedroom'
#     print(f'root dir {root_directory}')
#     count_files_in_subfolders(root_directory)

#    root_directory = r'/home/yl962/rds/hpc-work/VRR/Data/VRR_Patches/2024-09-12/crytek_sponza'
#    print(f'root dir {root_directory}')
#    count_files_in_subfolders(root_directory)