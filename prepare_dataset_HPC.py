import os
import zipfile
import random
import shutil
from pathlib import Path
from utils import scene_velocity_dicts, VRRML
from create_train_data import rename_subfolders_for_scene


def extract_zip(scene, zip_path, extract_to):
    """Extract zip file to a specific directory"""
    
    exist = os.path.exists(f'{extract_to}/{scene}')
    if exist:
        print(f'{extract_to}/{scene} exist, return')
        return 
    print(f'extracting zip folder for {scene}...')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    print(f'finish extracting...')
    


def create_split_folders(base_path):
    """Create folders for train, validation, and test sets"""
    val_dir = os.path.join(base_path, 'validation')
    test_dir = os.path.join(base_path, 'test')
    os.makedirs(val_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    return val_dir, test_dir




def copy_files(file_list, dest_folder, MOVE=False):
    """Copy a list of files to a destination folder, maintaining folder structure"""
    # count = 0
    for image in file_list:
        dest_path = os.path.join(dest_folder, os.path.relpath(image, start=image.parents[2]))
        # count += 1
        # if count > 2:
        #     break
        if MOVE:
            # shutil.move(image, dest_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(str(image), dest_path)  # Move the file instead of copying
    # print(f'moved {len(file_list)} to {dest_folder}')



def split_data(patch_dir, val_dir, test_dir, train_ratio=0.8, val_ratio=0.10, MOVE=False):
    for path_folder in os.listdir(patch_dir):
        print(f'\n====================== path_folder {path_folder} ======================')
        path_folder_full = os.path.join(patch_dir, path_folder)
        print(f'{os.listdir(path_folder_full)}')
        # Iterate over the bitrate subfolders (e.g., 720x30x500)
        for bitrate_folder in os.listdir(path_folder_full):
            # print(f'bitrate_folder {bitrate_folder}')
            # if 'kbps' in bitrate_folder:
            #     print(f'bitrate_folder {bitrate_folder} not valid')
            #     continue

            # print(f'bitrate_folder {bitrate_folder} valid')

            # fps_target, resolution_target, bitrate = map(int, bitrate_folder.split('x'))
            bitrate_path = os.path.join(path_folder_full, bitrate_folder)
       
            all_files = list(Path(bitrate_path).rglob('*.*')) # Get all files in the directory
            random.shuffle(all_files)
            total_files = len(all_files)
            train_size = int(train_ratio * total_files)
            val_size = int(val_ratio * total_files)
            
            val_files = all_files[train_size:train_size + val_size]
            test_files = all_files[train_size + val_size:]
            print(f'\nall_images {total_files}, train_size {train_size}, val_size {val_size}, test_size {total_files - train_size - val_size}')
            print(f'bitrate_path {bitrate_path}')
            # print(f'val_dir {val_dir}')
            # print(f'test_dir {test_dir}')

            copy_files(val_files, val_dir, MOVE=MOVE)
            copy_files(test_files, test_dir, MOVE=MOVE)
            # print(f'moved {len(val_files)} validation data, {len(test_files)} test data.')



def process_and_split(scene, zip_file, extract_path, MOVE=False):
    """Main function to process and split data"""
    extract_zip(scene, zip_file, extract_path)

    # assign label
    velocity_dict = scene_velocity_dicts[scene]
    rename_subfolders_for_scene(scene, velocity_dict, extract_path, bitrates, MOVE=MOVE)
    
    val_dir, test_dir = create_split_folders(extract_path)
    # print(f'val_dir, test_dir {val_dir, test_dir}')

    split_data(f'{extract_path}/{scene}', val_dir, test_dir, MOVE=MOVE)

    # # zip original folder
    # print(f'start zipping file')
    # shutil.make_archive(f'{extract_path}/{scene}', 'zip', extract_path)
    





# all data are in zip folders, e.g. bistro.zip
# unzip and randomly sample to train, test, and validation dataset
if __name__ == "__main__":

    bitrates = [500, 1000, 1500, 2000]
    # bitrates = [500,]
    # invalid_bitrates = 
    MOVE = True # True False
    zip_base_path = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\HPC\cleaned_patches_HPC\cleaned_patches'

    scene_arr = [
             'crytek_sponza', 'gallery', 
             'living_room', 'lost_empire', 
             'room', 'sibenik', 'suntemple', 
             'suntemple_statue']
    for scene in scene_arr:
        zip_file_path = f'{zip_base_path}/{scene}.zip'  # Path to your zip file
        extract_path = f'{VRRML}/ML'  # Path to extract data temporarily (RAM disk or other)

        # Process the data and split into train, validation, test sets
        process_and_split(scene, zip_file_path, extract_path, MOVE=MOVE)