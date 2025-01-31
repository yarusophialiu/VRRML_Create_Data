import cv2
import numpy as np
import os
import shutil
import secrets
from utils_windows import *
import datetime
import torch
import torchvision.transforms as transforms


def rename_subfolders_for_scene(scene, velocity_dict, base_dir, bitrates, MOVE=False):
    scene_folder = os.path.join(base_dir, scene)
    print(f'scene_folder {scene_folder}')
    if not os.path.exists(scene_folder):
        print(f"Scene folder '{scene_folder}' does not exist. Skipping.")
        return
    
    for sequence_name, params_list in velocity_dict.items(): # bistro_path1_seg1_1: [[xxx], [xxx], [xxx]]
        sequence_path = f'{scene_folder}/{scene}_{sequence_name}'
        if not os.path.exists(sequence_path):
            # print(f"Folder '{sequence_path}' does not exist. Skipping.")
            continue
            
        for i, bitrate in enumerate(bitrates):
            print(f'creat train bitrate {bitrate}')
            # Subfolder to find, e.g., '500kbps', '1000kbps'
            old_folder_path = f'{sequence_path}/{bitrate}kbps'

            if not os.path.exists(old_folder_path):
                print(f"Folder '{bitrate}kbps' does not exist. Skipping.\n")
                continue

            optimal_fps, optimal_resolution = params_list[i]
            print(f'optimal_fps, optimal_resolution {optimal_fps, optimal_resolution}')
            new_folder_name = f"{optimal_resolution}x{optimal_fps}x{bitrate}"
            new_folder_path = os.path.join(sequence_path, new_folder_name)
            
            # Rename the folder, not move
            if os.path.exists(new_folder_path):
                print(f'rename folder exist, continue.')
                continue

            print(f"Renaming {old_folder_path}")
            print(f"to {new_folder_path}\n")
            if MOVE:
                shutil.move(old_folder_path, new_folder_path)

            # if MOVE:
            #     destination = f'{training_data_dir}/{scene}/{scene}_{sequence_name}/{new_folder_name}'
            #     print(f'source {old_folder_path}')
            #     print(f'destination {destination}\n')
            #     # shutil.move(old_folder_path, destination)

                

# for each path e.g. suntemple_statue_path1_seg1_1, find optimal label for each bitrate, and move
if __name__ == "__main__":
    scene_velocity_dicts = {
        # 'bistro': bistro_max_comb_per_sequence,
        # 'suntemple': suntemple_max_comb_per_sequence,
        'suntemple_statue': suntemple_statue_max_comb_per_sequence
    }

    bitrates = [500, 1000, 1500, 2000]

    patch_dir = f'{VRR_Patches}/test' # scenes
    training_data_dir = f'{VRRML}/train'
    MOVE = False # True False

    for scene, velocity_dict in scene_velocity_dicts.items():
        print(f'=============== scene {scene} ===============')
        rename_subfolders_for_scene(scene, velocity_dict, patch_dir, bitrates, MOVE=MOVE)
    





