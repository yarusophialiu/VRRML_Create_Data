import os
import shutil
from utils import *



def restructure_data(source_dir, destination_dir):
    # Traverse through each path_bitrate subfolder
    for root in os.listdir(source_dir):
        print(f'root {root}')
        last_part = os.path.basename(root)
        parts = last_part.split('_')
        res_target = int(parts[-3])
        fps_target = int(parts[-2])
        # print(f'fps_target, res_target {fps_target, res_target}')

        # Create a new subfolder name based on resolution and fps targets
        new_subfolder = f"{res_target}x{fps_target}"
        new_subfolder_path = os.path.join(destination_dir, new_subfolder)
        print(f'new_subfolder_path {new_subfolder_path}') if not os.path.exists(new_subfolder_path) else None
        os.makedirs(new_subfolder_path, exist_ok=True)

        count = 0
        path_bitrate_dir = f'{source_dir}/{root}'
        for file in os.listdir(path_bitrate_dir):
            # print(f'file {file}')
            # Extract the relevant parts of the filename
            filename_parts = file.split('_')
            fps = int(filename_parts[1])
            res = int(filename_parts[2])
            # print(f'fps, res {fps, res}')
            
            # Move the PNG file to the new subfolder
            source_file_path = os.path.join(path_bitrate_dir, file)
            destination_file_path = os.path.join(new_subfolder_path, file)
            if COPY:
                shutil.copy(source_file_path, destination_file_path)
            # print(f"Copied {file} to {new_subfolder_path}")

            # count += 1
            # if count > 0:
            #     break

    print("All files have been copied to their respective subfolders.")







# categorize pngs to res_target x fps_target
if __name__ == "__main__":
    COPY = False # True False
    subfolder = 'ML_smaller'
    type = 'validation'
    src_dir = f'{VRRML}/{subfolder}/{type}_bitratelabel'
    dest_dir = f'{VRRML}/{subfolder}/{type}_label'
    os.makedirs(dest_dir, exist_ok=True)

    restructure_data(src_dir, dest_dir)


