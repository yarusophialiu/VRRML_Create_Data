import os
import shutil

def organize_images_by_fps(source_folder):
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder {source_folder} does not exist.")
        return
    
    # Iterate over all files in the source folder
    # for fps in range(4, 182):
    fpsfolder = source_folder
    for filename in os.listdir(fpsfolder):
        if filename.endswith(".png"):  # Check if the file is an image
            # Extract fps from the filename
            parts = filename.split('_')
            if len(parts) > 3:
                fps = parts[3]  # Assuming the fps is always in the third position
                
                # Define the target folder name based on fps
                target_folder = os.path.join(source_folder, f"fps{fps}")
                # print(f'target_folder {target_folder}')
                
                # Create the target folder if it does not exist
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                    
                # Construct the source and destination file paths
                src_path = os.path.join(fpsfolder, filename)
                dst_path = os.path.join(target_folder, filename)
                
                # Move the file
                shutil.move(src_path, dst_path)
                # print(f"Moved {filename} to {target_folder}")
            else:
                print(f"Filename {filename} does not conform to expected format.")
        else:
            print(f"Ignored non-image file: {filename}")

import os
import shutil

def move_first_files(source_folder, number_of_files=350):
    # Iterate over all directories in the source folder
    for subdir in os.listdir(source_folder):
        fps_folder_path = os.path.join(source_folder, subdir)
        # Check if it's a directory and matches the fps naming pattern
        if os.path.isdir(fps_folder_path) and subdir.startswith("fps"):
            # Create a new subdirectory for the first 65 files
            new_folder_path = os.path.join(source_folder, f"first70_{subdir}")
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)

            # Get all files in the fps directory
            files = [f for f in os.listdir(fps_folder_path) if os.path.isfile(os.path.join(fps_folder_path, f))]
            # Sort files to ensure consistency, optional
            files.sort()

            # Move the first 65 files to the new directory
            for file in files[:number_of_files]:
                src_path = os.path.join(fps_folder_path, file)
                dst_path = os.path.join(new_folder_path, file)
                shutil.move(src_path, dst_path)
                # print(f"Moved {file} from {subdir} to {new_folder_path}")



def count_files_in_subfolders(source_folder):
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"The source folder {source_folder} does not exist.")
        return
    
    # Iterate over all items in the source folder
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        # Check if the item is a directory
        if os.path.isdir(item_path):
            # List only files within this directory
            files = [f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))]
            # Print the directory name and the number of files it contains
            print(f"Subfolder {item} contains {len(files)} files.")




base_directory = 'C:/Users/15142/Desktop/VRR/VRR_Patches/suntemple_tonemap/2024-04-23/'
image_folder = f'{base_directory}/train_data/reference'
# organize_images_by_fps(image_folder)
# move_first_files(image_folder)
count_files_in_subfolders(image_folder)

