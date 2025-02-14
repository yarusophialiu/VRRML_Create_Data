import os
import zipfile
import random
import shutil
from pathlib import Path
from utils import scene_velocity_dicts, drop_JOD_dicts, VRRML



def rename_subfolders_for_scene(scene, velocity_dict, scene_folder, bitrates, dest_path, MOVE=False, FRAMENUMBER_SHOW=False):
    # print(f'scene_folder {scene_folder}')
    if not os.path.exists(scene_folder):
        # print(f"Scene folder '{scene_folder}' does not exist. Skipping.")
        return
    
    count = 0
    for sequence_name, params_list in velocity_dict.items(): # bistro_path1_seg1_1: [[xxx], [xxx], [xxx]]
        sequence_path = f'{scene_folder}/{scene}_{sequence_name}'
        # print(f'path folder {scene}_{sequence_name}')
        # print(f'sequence_path {sequence_path}')
        if not os.path.exists(sequence_path):
            # print(f"Folder '{sequence_path}' does not exist. Skipping.")
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
                newfilename = f'{parts[0]}_166_1080_{bitrate}_{scene}_{sequence_name}_{parts[1]}' if not FRAMENUMBER_SHOW else \
                              f'{parts[0]}_166_1080_{bitrate}_{parts[1]}_{scene}_{sequence_name}_{parts[2]}'
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

    # titanium
    reference_dir  = r'D:\VRR_data\VRR_Patches\2025-02-10'
    dest_path = r'D:\VRR_data\VRRML\ML\consecutive_patches64x64'

    # reference_dir  = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\2025-01-30'
    # dest_path = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\reference_new64'

    scene_arr = [
            'bedroom', 
            'bistro',
            'crytek_sponza', 'gallery', 
            'living_room', 
            'lost_empire', 
            'room', 
            'suntemple', 
            #  'suntemple_statue',
            # 'sibenik'
             ]
    COPY = True # False True
    FRAMENUMBER_SHOW = True
    # bistro_max_comb_per_sequence = {'path1_seg1_1': [[30, 1080], [40, 1080], [50, 1080], [50, 1080]],} 
    #                                 # 'path1_seg1_2': [[70, 720], [80, 720], [80, 1080], [80, 1080]], 'path1_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[50, 720], [70, 1080], [80, 1080], [80, 1080]], 'path1_seg2_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[50, 720], [50, 1080], [50, 1080], [60, 1080]], 'path1_seg3_2': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path1_seg3_3': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[60, 720], [80, 720], [80, 720], [80, 1080]], 'path2_seg1_2': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path2_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[60, 720], [80, 720], [80, 1080], [80, 1080]], 'path2_seg2_2': [[90, 480], [110, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[120, 360], [120, 480], [120, 480], [120, 720]], 'path2_seg3_1': [[40, 720], [50, 1080], [60, 1080], [60, 1080]], 'path2_seg3_2': [[80, 720], [90, 720], [110, 720], [120, 720]], 'path2_seg3_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[90, 720], [100, 720], [110, 720], [120, 720]], 'path3_seg1_2': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg2_1': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path3_seg2_2': [[80, 720], [100, 720], [110, 720], [120, 720]], 'path3_seg2_3': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[80, 720], [90, 720], [110, 720], [120, 1080]], 'path3_seg3_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg3_3': [[120, 480], [120, 480], [120, 480], [120, 720]], 'path4_seg1_1': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path4_seg1_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path4_seg2_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_3': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg3_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg3_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path5_seg1_1': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path5_seg1_2': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path5_seg1_3': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[80, 720], [90, 720], [120, 720], [120, 720]], 'path5_seg2_2': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg3_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]]}

    # scene_velocity_dicts = {'suntemple_statue': bistro_max_comb_per_sequence}
    for scene in scene_arr:
        scene_dir = f'{reference_dir}/reference_{scene}'
        velocity_dict = scene_velocity_dicts[scene] # drop_JOD_dicts[scene] scene_velocity_dicts[scene]
        # velocity_dict = drop_JOD_dicts[scene] # scene_velocity_dicts[scene]
        rename_subfolders_for_scene(scene, velocity_dict, scene_dir, bitrates, dest_path, MOVE=COPY)