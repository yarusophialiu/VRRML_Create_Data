import os
import zipfile
import random
import shutil
from pathlib import Path
from utils import scene_velocity_dicts, VRRML







def rename_subfolders_for_scene(scene, velocity_dict, scene_folder, bitrates, dest_path, MOVE=False):
    print(f'scene_folder {scene_folder}')
    if not os.path.exists(scene_folder):
        print(f"Scene folder '{scene_folder}' does not exist. Skipping.")
        return
    
    count = 0
    for sequence_name, params_list in velocity_dict.items(): # bistro_path1_seg1_1: [[xxx], [xxx], [xxx]]
        sequence_path = f'{scene_folder}/{scene}_{sequence_name}'
        print(f'sequence_path {sequence_path}')
        if not os.path.exists(sequence_path):
            print(f"Folder '{sequence_path}' does not exist. Skipping.")
            continue
            
        for i, bitrate in enumerate(bitrates):
            optimal_fps, optimal_resolution = params_list[i]
            # print(f'================= bitrate {bitrate}, i {i}, optimal_fps, optimal_resolution {optimal_fps, optimal_resolution} =================')
            new_folder_name = f"{optimal_resolution}x{optimal_fps}"
            # print(f'new_folder_name {new_folder_name}')
            # new_folder_name = f"{scene}_{sequence_name}_{optimal_resolution}_{optimal_fps}_{bitrate}"
            new_folder_path = os.path.join(dest_path, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)
            # print(f'new_folder_path {new_folder_path}\n')

            # loop through patches and copy to destionation
            # with fps, resolution, velocity, bitrate
            for filename in os.listdir(sequence_path):
                parts = filename.split("_")
                newfilename = f'{parts[0]}_166_1080_{bitrate}_{parts[1]}'
                # print(f'filename {filename}')
                # print(f'newfilename {newfilename}')

                old_file_path = f'{sequence_path}/{filename}'
                new_file_path= f'{new_folder_path}/{newfilename}'
                # print(f"Renaming {old_folder_path}")
                # print(f"to {new_folder_path}\n")
                # existold = os.path.exists(old_file_path)
                # exist = os.path.exists(new_file_path)
                # print(f'exist old {existold} exist new {exist}')
                if MOVE and (not os.path.exists(new_file_path)):
                    # print(f'move to {new_file_path}')
                    shutil.copy(old_file_path, new_file_path)
        #         break
        #     break
        # break



# all data are extracted from reference video
if __name__ == "__main__":
    bitrates = [500, 1000, 1500, 2000]
    reference_dir  = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\2024-09-19'
    dest_path = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\reference'
    scene_arr = ['bedroom']
    COPY = True # False True

    for scene in scene_arr:
        scene_dir = f'{reference_dir}/reference_{scene}'
        velocity_dict = scene_velocity_dicts[scene]
        rename_subfolders_for_scene(scene, velocity_dict, scene_dir, bitrates, dest_path, MOVE=COPY)