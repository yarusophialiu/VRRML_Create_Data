import os
import random
import shutil
from utils_windows import *


def creat_new_train_dir(old_train_dir, new_train_dir):
    for path_folder in os.listdir(old_train_dir):
        path_folder_path = os.path.join(old_train_dir, path_folder) # bedroom_path2_seg2_3
        print(f'=========== path_folder_path {path_folder_path} ===========')

        if os.path.isdir(path_folder_path):
            for bitrate_folder in os.listdir(path_folder_path): # 480x100x500
                bitrate_folder_path = os.path.join(path_folder_path, bitrate_folder)

                if os.path.isdir(bitrate_folder_path):
                    # Extract the metadata from the bitrate folder name (e.g., 720x30x500)
                    resolution_target, fps_target, bitrate = bitrate_folder.split('x')
                    print(f'resolution_target, fps_target, bitrate {resolution_target, fps_target, bitrate}')

                    # Create the new folder structure with path_bitrate naming
                    new_folder_name = f"{path_folder}_{resolution_target}_{fps_target}_{bitrate}"
                    new_folder_path = os.path.join(new_train_dir, new_folder_name)

                    # Create the new folder if it doesn't exist
                    if not os.path.exists(new_folder_path):
                        # print(f'make new_folder_path {new_folder_path}')
                        os.makedirs(new_folder_path)

                    # Get all patch files in the current bitrate folder
                    patches = [f for f in os.listdir(bitrate_folder_path) if os.path.isfile(os.path.join(bitrate_folder_path, f))]
                    selected_patches = random.sample(patches, num_patches)

                    # Copy selected patches to the new folder
                    for patch in selected_patches:
                        old_patch_path = os.path.join(bitrate_folder_path, patch)
                        new_patch_path = os.path.join(new_folder_path, patch)
                        # print(f'old_patch_path {old_patch_path}')
                        # print(f'new_patch_path {new_patch_path}')
                        if COPY:
                            shutil.copyfile(old_patch_path, new_patch_path)
                            # print(f'copied {num_patches} patches to {new_folder_path}')



if __name__ == "__main__":
    # src_train_dir = f'{VRRML}/ML/test'
    # dest_train_dir = f'{VRRML}/ML/test_bitratelabel'

    src_train_dir = f'{VRRML}/ML/validation'
    dest_train_dir = f'{VRRML}/ML/validation_bitratelabel'

    os.makedirs(dest_train_dir, exist_ok=True)
    num_patches = 20 # 200 for training data, 20 for val and test

    COPY = True # False
    creat_new_train_dir(src_train_dir, dest_train_dir)