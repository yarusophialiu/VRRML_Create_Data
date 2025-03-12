import os
import torch
import cv2
import datetime
from collections import Counter
import pandas as pd
import importlib.util
from utils import *
from extract_patch_h264_scene_8000 import get_random_patch, read_frame_velocity
import os
import shutil
import random


def generate_frame_indices(num_data_need, total_frames=276):
    """
    Generates a list of frame indices ensuring an even distribution.
    - If num_data_need < total_frames: Select unique frames.
    - If num_data_need >= total_frames: Distribute patches across all frames.
    """
    if num_data_need < total_frames:
        return np.random.choice(total_frames, num_data_need, replace=False).tolist()  # Select unique frames
    
    frame_indices = []
    patches_needed_per_frame = int(np.ceil(num_data_need / total_frames))
    
    for frame_id in range(total_frames):
        frame_indices.extend([frame_id] * patches_needed_per_frame)  # Assign patches to this frame
    np.random.shuffle(frame_indices)  # Shuffle to avoid sequential bias
    return frame_indices[:num_data_need]  # Ensure exact count


# def generate_patches(base_dir, path_name, , frame_indices, frame_velocity_path, patch_size=(64, 64), output_dir="output", scene=None):
def generate_patches(base_dir, path_name, frame_indices, frame_velocity_path, output_dir="output", patch_size=(64, 64),):
    """
    Generates patches from a video, allowing multiple patches from the same frame if needed.
    """
    video_path = f'{base_dir}/{path_name}/ref166_1080/refOutput.mp4'
    print(f'video_path {video_path}')
    cap = cv2.VideoCapture(video_path)    
    if not cap.isOpened():
        print("Error opening video file")
        return 0
    
    frame_generated = 0
    frame_patches_count = {i: frame_indices.count(i) for i in set(frame_indices)}  # Count patches per frame
    # print(f'set(frame_indices) {set(frame_indices)}')
    # print(f'frame_patches_count {frame_patches_count}')
    # print(f'frame_indices {len(frame_indices)}')
    frame_number = 0  # Decoded video frame index
    while cap.isOpened():
        if frame_number not in frame_patches_count:
            frame_number += 1
            if cap.grab():
                continue
            else:
                break
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = torch.from_numpy(frame).permute(2, 0, 1)  # Convert to PyTorch tensor (C, H, W)
        height, width = 1080, 1920
        
        for _ in range(frame_patches_count[frame_number]):  # Generate multiple patches from the same frame
            interpolated_patch, px, py = get_random_patch(width, height, patch_size, frame)
            # show_patch(interpolated_patch.permute(1,2,0))
            velocity = None
            if FRAME_VELOCITY:
                velocity = read_frame_velocity(frame_velocity_path, frame_number)
                # print(f'velocity {velocity}')
            # if PATCH_VELOCITY:
            #     motion_patch = find_motion_patch_h265(motion_video_path, fps, 166, frame_number, px, py, patch_size=patch_size)
            #     velocity = compute_velocity(motion_patch, motion_vector_path)
            if velocity is None:
                continue
            
            hex_unique_id = secrets.token_hex(4)
            path = f'{output_dir}/{hex_unique_id}_{int(velocity*1e5)}.png' if not FRAMENUMBER_SHOW else f'{output_dir}/{hex_unique_id}_{frame_number}_{int(velocity*1e5)}.png'
            # print(f'path {path}')
            if SAVE:
                to_pil = transforms.ToPILImage()
                interpolated_patch = to_pil(interpolated_patch)
                interpolated_patch.save(path, "png")
            
            frame_generated += 1
        frame_number += 1
    cap.release()
    return frame_generated


# Function to generate patches for each path in df_matching_results
# def extract_patches_from_paths(df_matching_results, num_data_need, base_directory, motion_vector_path, motion_video_path, frame_velocity_path, output_folder):
def extract_patches_from_paths(df_matching_results, num_data_need):
    patch_size = (PATCH_SIZE, PATCH_SIZE)  # Ensure PATCH_SIZE is defined
    extracted_patches = 0  # Counter for patches generated
    num_data_need_each_path = int(np.ceil(num_data_need / len(df_matching_results)))
    print(f'num_data_need_each_path {num_data_need_each_path}')
    
    for _, row in df_matching_results.iterrows():
        path_name = row["Path"]
        scene = row["Scene"]
        print(f'================ extract from {scene} ================')
        
        # Generate frame indices based on num_data_need
        frame_indices = generate_frame_indices(num_data_need_each_path)
        # print(f'frame_indices {len(frame_indices)},') # \n{frame_indices}
        frame_velocity_path = f'{VRR_Motion}/reference/magnitude_motion_per_frame/{scene}/{scene}_{path_name}_velocity_per_frame.txt'
        # print(f'frame_velocity_path {frame_velocity_path}')
        output_folder = f'{output_parent_folder}/reference_{scene}/{scene}_{path_name}'
        os.makedirs(output_folder, exist_ok=True)

        base_directory = f'{VRRMP4_reference}/{scene}'
        patch_generated = generate_patches(
            base_directory, f'{scene}_{path_name}',
            frame_indices, frame_velocity_path, output_dir=output_folder, patch_size=patch_size
        )
        
        extracted_patches += patch_generated  # Update count
        
        # Stop if we have extracted enough patches
        if extracted_patches >= num_data_need:
            break
    
        print(f"Total patches generated: {extracted_patches}")

# which paths, bitrate match the insufficient label
def get_matching_results(target_fps, target_resolution):
    matching_results = []
    # Iterate over the dictionary to find matching labels
    for scene in scenes:
        if DROPJOD:
            scene_path_labels = getattr(data_module, f'{scene}_comb_drop_JOD') # TODO change _comb_drop_JOD
        else:
            scene_path_labels = getattr(data_module, f'{scene}_max_comb_per_sequence')
        for path, labels in scene_path_labels.items():
            for bitrate_index, (fps, resolution) in enumerate(labels):
                if fps == target_fps and resolution == target_resolution:
                    bitrate = (bitrate_index + 1) * 500  # Convert index to bitrate (500, 1000, 1500, 2000)
                    matching_results.append((
                        scene,  # Scene name
                        path,       # Path name
                        bitrate,    # Bitrate
                        fps,        # FPS
                        resolution  # Resolution
                    ))
    return matching_results

def get_missing_data_list(df_subfolder_counts, num_data_each_label):
    df_subfolder_counts["Additional Data Needed"] = df_subfolder_counts["Image Count"].apply(
        lambda x: max(0, num_data_each_label - x)  # Ensure non-negative values
    )
    df_subfolder_counts[["Resolution", "FPS"]] = df_subfolder_counts["Subfolder"].str.split("x", expand=True).astype(int)
    df_missing_data = df_subfolder_counts[df_subfolder_counts["Additional Data Needed"] > 0]
    # print(f'df_missing_data\n{df_missing_data}')

    missing_data_list = [
        (row["Additional Data Needed"], row["Resolution"], row["FPS"])
        for _, row in df_missing_data.iterrows()
    ]
    return missing_data_list

def get_excess_data_list(df_subfolder_counts, num_data_each_label):
    df_subfolder_counts[["Resolution", "FPS"]] = df_subfolder_counts["Subfolder"].str.split("x", expand=True).astype(int)
    df_excess_data = df_subfolder_counts[df_subfolder_counts["Image Count"] > num_data_each_label].copy()
    # Calculate the number of extra data that should be deleted
    df_excess_data["Extra Data to Delete"] = df_excess_data["Image Count"] - num_data_each_label
    print(f'df_excess_data\n{df_excess_data}')
    df_excess_data = df_excess_data[["Resolution", "FPS", "Extra Data to Delete"]]

    excess_data_list = [
        (row["Extra Data to Delete"], row["Resolution"], row["FPS"])
        for _, row in df_excess_data.iterrows()
    ]
    print(f'excess_data_list\n{excess_data_list}')
    return excess_data_list

# count fpsxresolution: how many data belongs to this label
def save_training_data_to_csv(training_folder):
    # Dictionary to store counts
    subfolder_counts = Counter()
    for subfolder in os.listdir(training_folder):
        subfolder_path = os.path.join(training_folder, subfolder)
        if os.path.isdir(subfolder_path):  # Ensure it's a directory
            # Count number of images in the subfolder (assuming images are files)
            image_count = len([f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))])
            subfolder_counts[subfolder] = image_count

    # Convert to DataFrame and sort by count (descending)
    df_subfolder_counts = pd.DataFrame(subfolder_counts.items(), columns=["Subfolder", "Image Count"])
    df_subfolder_counts = df_subfolder_counts.sort_values(by="Image Count", ascending=False)

    total_images = df_subfolder_counts["Image Count"].sum()
    print("Total number of images:", total_images) # 351748
    num_rows = len(df_subfolder_counts)
    print("Number of rows:", num_rows)
    num_data_each_label =  int(total_images/num_rows)
    df_subfolder_counts.to_csv('train_data_lable_count.csv', index=False)
    return num_data_each_label

def move_excess_data(training_folder, excess_data_list, excess_data_folder):
    """
    Moves excess data from training subfolders to an 'excess_train_data' folder.
    training_folder (str): The path to the main training directory.
    excess_data_list (list of tuples): List containing (num_to_delete, resolution, fps).
    excess_data_folder (str): The folder where excess data will be moved.
    """
    os.makedirs(excess_data_folder, exist_ok=True)

    for num_to_delete, resolution, fps in excess_data_list:
        print(f'\nnum_to_delete, resolution, fps {num_to_delete, resolution, fps}')
        subfolder_name = f"{resolution}x{fps}"
        subfolder_path = os.path.join(training_folder, subfolder_name)
        excess_subfolder_path = os.path.join(excess_data_folder, subfolder_name)
        
        if not os.path.exists(subfolder_path):
            print(f"Skipping {subfolder_name}: Folder does not exist.")
            continue
        os.makedirs(excess_subfolder_path, exist_ok=True)

        image_files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
        # Ensure we don't delete more files than available
        num_to_delete = min(num_to_delete, len(image_files))
        files_to_move = random.sample(image_files, num_to_delete)

        # Move the files
        for file_name in files_to_move:
            src_path = os.path.join(subfolder_path, file_name)
            dst_path = os.path.join(excess_subfolder_path, file_name)
            shutil.move(src_path, dst_path)

        print(f"Moved {num_to_delete} files from {subfolder_name} to {excess_subfolder_path}")

def copy_extracted_patches(source_folder, training_folder):
    """
    Moves extracted patches from the source folder to their corresponding subfolders in the training folder.
    extracted more patches for training_folders/subfolder that needs more data, saved in source_folder
    Parameters:
        source_folder (str): The folder where newly extracted patches are stored.
        training_folder (str): The destination training folder.
    """
    for subfolder_name in os.listdir(source_folder):
        print(f'============== {subfolder_name} ==============')
        source_subfolder_path = os.path.join(source_folder, subfolder_name)
        target_subfolder_path = os.path.join(training_folder, subfolder_name)

        if not os.path.isdir(source_subfolder_path):
            continue
        num_files_copied = 0
        # Move files from the source subfolder to the corresponding training subfolder
        for file_name in os.listdir(source_subfolder_path):
            src_path = os.path.join(source_subfolder_path, file_name)
            dst_path = os.path.join(target_subfolder_path, file_name)
            print(f'src_path {src_path}')
            print(f'dst_path {dst_path}')
            shutil.copyfile(src_path, dst_path)
            num_files_copied += 1

        print(f"Copied {num_files_copied} data from {source_subfolder_path} to {target_subfolder_path}")


def get_matching_fps_resolution_bitrate(scene, path, df_matching_results):
    match = df_matching_results[(df_matching_results['Scene'] == scene) & 
                                (df_matching_results['Path'] == path)]
    if not match.empty:
        return match.iloc[0]['FPS'], match.iloc[0]['Resolution'], match.iloc[0]['Bitrate']
    return None, None, None

def process_images(source_folder, dest_folder, df_matching_results):
    for scene_path in os.listdir(source_folder):
        full_scene_path = os.path.join(source_folder, scene_path)
        
        if not os.path.isdir(full_scene_path):
            continue
        
        scene, path = scene_path.split("_", 1)  # Extract scene and path
        target_fps, target_resolution, bitrate = get_matching_fps_resolution_bitrate(scene, path, df_matching_results)

        if target_fps is None or target_resolution is None or bitrate is None:
            # print(f"Skipping {scene_path}, no matching FPS/Resolution/Bitrate found.")
            continue
        
        target_folder = os.path.join(dest_folder, f"{target_resolution}x{target_fps}")
        os.makedirs(target_folder, exist_ok=True)
        
        for filename in os.listdir(full_scene_path):
            if filename.endswith(".png"):  # Assuming images are PNG files
                parts = filename.split("_") # hex_id, framenumber, velocity
                if FRAMENUMBER_SHOW:
                    new_filename = f"{parts[0]}_166_1080_{bitrate}_{parts[1]}_{scene}_{path}_{parts[2]}"
                else:
                    new_filename = f"{parts[0]}_166_1080_{bitrate}_{scene}_{path}_{parts[1]}"
                src_path = os.path.join(full_scene_path, filename)
                dest_path = os.path.join(target_folder, new_filename)
                shutil.copy(src_path, dest_path)
            # break

# 0048e3e3_166_1080_1500_134_bedroom_path2_seg2_2_186.png
# get csv file in VRRML/test
if __name__ == "__main__":
    # count labels and how many training data in each label
    
    training_folder = r"D:\VRR_data\VRRML\ML\frame-velocity\train_single_64x64\train"  # Change this to your actual folder path
    excess_data_folder = r"D:\VRR_data\VRRML\ML\frame-velocity\excess_train_single_64x64"
    # num_data_each_label = save_training_data_to_csv(training_folder)

    csv_file_path = 'train_single_64x64_dropjod_lable_count.csv' # TODO change dropjod, maxjod
    df_subfolder_counts = pd.read_csv(csv_file_path)
    total_images = df_subfolder_counts["Image Count"].sum()
    num_rows = len(df_subfolder_counts)
    print(f"Total number of images: {total_images}, number of rows: {num_rows}")
    num_data_each_label =  int(total_images/num_rows)
    print(f"Number of data for each label:", num_data_each_label)

    FRAME_VELOCITY = True # not support patch velocity
    FRAMENUMBER_SHOW = True
    SAVE = True
    EXTRACT_PATCHES = False # True False
    LABEL_DATA = True
    DROPJOD = True
    scenes = [
                'bedroom', 
                'bistro', 'crytek_sponza', 'gallery', 'living_room', 'lost_empire', 'room', 'suntemple',
                
                # 'sibenik','suntemple_statue' 
            ]
    spec = importlib.util.spec_from_file_location("data_module", 'utils.py')
    data_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(data_module)
    PATCH_SIZE = 64

    # # drop excessive data 
    # # TODO: check if excess_data_list is correct
    # excess_data_list = get_excess_data_list(df_subfolder_counts, num_data_each_label)
    # move_excess_data(training_folder, excess_data_list, excess_data_folder)
   
   
    current_date = datetime.date.today()
    # output_parent_folder = f'{VRR_Patches}/{current_date}_patch{PATCH_SIZE}x{PATCH_SIZE}'
    output_parent_folder = r'D:\VRR_data\VRR_Patches\2025-03-11_patch64x64'
    output_labeled_data_path = f'{output_parent_folder}_labeled_data'
    output_labeled_data_path = r'D:\VRR_data\VRR_Patches\2025-03-12_patch64x64_labeled_data'

    if EXTRACT_PATCHES or LABEL_DATA:
        # list of labels whose data is insufficient
        missing_data_list = get_missing_data_list(df_subfolder_counts, num_data_each_label)
        for item in missing_data_list: # item: 9047, 60, 864
            num_data_need = item[0] # 7810
            target_fps = item[2]
            target_resolution = item[1]
            print(f'num_data_need, target_fps, target_resolution {num_data_need, target_fps, target_resolution}\n')
            # find all scene-paths that have the required ground truth label
            matching_results = get_matching_results(target_fps, target_resolution) # used scenes [('bedroom', 'path2_seg2_2', 1500, 100, 480),...]
            df_matching_results = pd.DataFrame(matching_results, columns=["Scene", "Path", "Bitrate", "FPS", "Resolution"])
            print(f'df_matching_results \n{df_matching_results}')
            if EXTRACT_PATCHES:
                extract_patches_from_paths(df_matching_results, num_data_need)
            if LABEL_DATA:
                print(f'\nStart labeling data')
                for scene in scenes:
                    print(f'============= {scene} =============')
                    process_images(f'{output_parent_folder}/reference_{scene}', f'{output_labeled_data_path}', df_matching_results)
            # break

    # # move insufficient data
    # # source_folder = r"D:\VRR_data\VRR_Patches\2025-03-10_patch64x64_labeled_data"
    # copy_extracted_patches(dest_path, training_folder)
