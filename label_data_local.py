import os
import shutil
import datetime
from utils import *

def delete_empty_folders(root_folder):
    # Walk through the directory tree starting from root_folder
    for folder_name, _, _ in os.walk(root_folder, topdown=False):
        # Check if the folder is empty
        if not os.listdir(folder_name):
            # If the folder is empty, delete it
            os.rmdir(folder_name)
            print(f"Deleted empty folder: {folder_name}")


def copy_files(bitrate, fps, resolution, source_folder, motion_file):
    # find velocity
    motion = compute_motion(motion_file) * 1000
    folder_name = f"{resolution}x{fps}"
    # print(f'folder_name {folder_name}')
    output_folder = os.path.join(f'{source_folder}', folder_name)
    os.makedirs(output_folder, exist_ok=True) 
    bitrate_folder = os.path.join(source_folder, f'{bitrate}kbps')
    

    for file_name in os.listdir(bitrate_folder):  # Iterate over files in source folder
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):  # Check if file is an image
            index_png = file_name.find(".png")
            name_before_png = file_name[:index_png]
            # print(f'name {name_before_png}')
            source_file_path = os.path.join(bitrate_folder, file_name)  # Source file path
            destination_file_path = os.path.join(f"{source_folder}/{folder_name}", f'{name_before_png}_{int(motion)}.png')
            shutil.move(source_file_path, destination_file_path)  # Copy file to destination folder
            # print(f'destination_file_path {destination_file_path}')





def move_subfolder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for item in os.listdir(input_folder):
        item_path = os.path.join(input_folder, item)
        # print(f'item_path {item_path}') # scene/360x80

        output_path = os.path.join(output_folder, item) # e.g. train/360x720
        os.makedirs(output_path, exist_ok=True) # 很重要，不然回file not found error
        # print(f'output_path {output_path}')
        for filename in os.listdir(item_path): # ~.png
            # print(f'filename {filename}')
            file_path = os.path.join(item_path, filename)
            # print(f'file_path {file_path}')
            if os.path.isfile(file_path):
                # Move the file to the output directory
                output_file_path = os.path.join(output_path, filename)
                # print(f'output_file_path {output_file_path}')
                if os.path.exists(output_file_path):
                    print(f"File '{filename}' already exists in the output directory.")
                else:
                    shutil.move(file_path, output_file_path)
                    # print(f"File '{filename}' moved to '{output_path}'.")

        # Check if the item is a directory
        # if os.path.isdir(item_path):
        #     # Move the subfolder to the output directory
        #     output_path = os.path.join(output_folder, item)
        #     print(f'output_path {output_path}')

        #     os.makedirs(output_path, exist_ok=True)
        #     shutil.move(item_path, output_path)





# 1: label paches's folder, e.g. from 2000kbps to 720x80
# 2: move all folders scene/360x30 to a single folder called train
if __name__ == "__main__":
    # Loop through all combinations of bitrates, fps_arr, and resolution_arr
    base_folder = f'C:/Users/15142/Desktop/VRR/VRR_Patches/'
    source_date = '2024-05-26'
    motion_folder = 'C:/Users/15142/Desktop/VRR/VRR_Motion/data'
    motion_file = f'{motion_folder}/bistro_glasses2_160_1080_8000.txt'


    # scene_arr = ["test"]
    scene_arr = [
                 'bistropath_one1', 
                 'bistropath_one2', 'bistropath_three1', 'bistropath_three2', 'bistro_glasses2', \
                 'breakfast_room_two1', 'lost_empire_three1',  'sponza_three1', \
                  'paint2', 'room1', 'room2', \
                  'suntemple1', 'suntemple2', 'suntemple_statue2']
    # scene_arr = ["bistropath_one1"]

    COMBINE_DATA = True # True, False
    if COMBINE_DATA:
        for scene in scene_arr:
            print(f'scene {scene}')
            source_folder = f"{base_folder}/{source_date}/scene/{scene}"
            current_date = datetime.date.today()
            # print(f'current_date {current_date}')
            destination_folder = f"{base_folder}/{current_date}/train/"
            # os.makedirs(destination_folder, exist_ok=True)
            move_subfolder(source_folder, destination_folder)

    LABEL_DATA = False # True, False
    # # scene = 'test'
    # # Define the bitrates, fps_arr, and resolution_arr
    bitrates = [2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000]
    # scene_arr = ["breakfast_room_two1", "sponza_three1", "lost_empire_three1", "room1", "room2", "paint2", \
    #              "suntemple1", "suntemple2"]
    scene_arr = [
                #  'bistropath_one1', 
                'bistropath_one2', 'bistropath_three1', 'bistropath_three2', 'bistro_glasses2', \
                 'breakfast_room_two1', 'lost_empire_three1',  'sponza_three1', \
                  'paint2', 'room1', 'room2', \
                  'suntemple1', 'suntemple2', 'suntemple_statue2']
    scene_arr = ["lost_empire_three1"]

    all_fps_arr = {
        "bistropath_one1": [40, 40, 40, 40, 40, 60, 60, 90, 80, 80, 90, 100, 100, ],
        "bistropath_one2": [40, 40, 50, 60, 80, 60, 80, 80, 80, 80, 80, 80, 80, ],
        "bistropath_three1": [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, ],
        "bistropath_three2": [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, ],
        "bistro_glasses2": [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, ],
        "breakfast_room_two1": [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, ],
        "sponza_three1": [80, 80, 80, 80, 80, 80, 80, 80, 120, 120, 120, 120, 120, ], 
        "lost_empire_three1": [80, 80, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, ], 
        "room1": [90, 110, 110, 110, 110, 120, 120, 120, 120, 120, 120, 120, 120, ], 
        "room2": [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, ], 
        "paint2": [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, ], 
        "suntemple1": [100, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, ], 
        "suntemple2": [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, ], 
        "suntemple_statue2": [80, 80, 80, 80, 80, 120, 120, 120, 120, 120, 120, 120, 120,]
    }

    all_resolution_arr = {
        "bistropath_one1": [864, 864, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, ],
        "bistropath_one2": [864, 864, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, ],
        "bistropath_three1": [720, 720, 864, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, ],
        "bistropath_three2": [360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, ],
        "bistro_glasses2": [360, 720, 720, 720, 864, 720, 720, 720, 864, 864, 864, 720, 720, ],
        "breakfast_room_two1": [864, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, ],
        "sponza_three1": [720, 864, 864, 864, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, ], 
        "lost_empire_three1": [864, 864, 864, 864, 864, 864, 864, 1080, 1080, 1080, 1080, 1080, 1080, ], 
        "room1": [720, 720, 864, 864, 864, 864, 864, 1080, 1080, 1080, 1080, 1080, 1080, ], 
        "room2": [480, 720, 720, 864, 864, 864, 864, 1080, 1080, 1080, 1080, 864, 864, ], 
        "paint2": [480, 480, 480, 480, 480, 480, 480, 720, 720, 720, 720, 720, 720, ], 
        "suntemple1": [720, 720, 864, 864, 864, 864, 864, 1080, 1080, 1080, 1080, 1080, 1080, ], 
        "suntemple2": [480, 720, 720, 720, 864, 864, 864, 864, 1080, 1080, 1080, 1080, 1080, ], 
        "suntemple_statue2": [720, 864, 864, 1080, 864, 864, 1080, 1080, 1080, 720, 1080, 1080, 1080, ]
    }

    # fps_arr = [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80]
    # resolution_arr = [360, 720, 720, 720, 864, 720, 720, 720, 864, 864, 864, 720, 720]
    # bitrates = [2000, 2500, 3000]
    # fps_arr = [80, 80, 80]
    # resolution_arr = [360, 720, 720]
    if LABEL_DATA:
        for scene in scene_arr:
            print(f'scene {scene}')
            source_folder = f'{base_folder}/{source_date}/scene/{scene}'
            fps_arr = all_fps_arr[scene]
            resolution_arr = all_resolution_arr[scene]
            for bitrate, fps, resolution in zip(bitrates, fps_arr, resolution_arr):
                print(f'bitrate, fps, resolution {bitrate, fps, resolution}')
                copy_files(bitrate, fps, resolution, source_folder, f'{motion_folder}/{scene}_160_1080_8000.txt')

                bitrate_folder = os.path.join(source_folder, f'{bitrate}kbps')
                delete_empty_folders(bitrate_folder)