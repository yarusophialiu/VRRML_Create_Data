import cv2
import numpy as np
import os
import secrets
from utils import *
import datetime
import argparse
import torch
import torchvision.transforms as transforms
from prepare_dataset_reference import rename_subfolders_for_scene


def get_random_patch(width, height, patch_size, interpolated_img):
    max_x = width - patch_size[1]
    max_y = height - patch_size[0]
    x = np.random.randint(0, max_x + 1) 
    y = np.random.randint(0, max_y + 1)
    # print(f'x, y {x, y}')

    interpolated_patch = interpolated_img[:, y:y+patch_size[0], x:x+patch_size[1]]
    return interpolated_patch, x, y



def read_motion_vectors(file_path):
    max_x = float('-inf')  # Initialize max_x with the smallest possible value
    max_y = float('-inf')  # Initialize max_y with the smallest possible value

    # Open the file and read the motion vector pairs
    with open(file_path, 'r') as file:
        lines = file.readlines()

        # Convert the first line to a float and assign it to max_x
        max_x = float(lines[0].strip())

        # Convert the second line to a float and assign it to max_y
        max_y = float(lines[1].strip())
    return round(max_x, 5), round(max_y, 5)



def compute_velocity(patch, motion_vector_path):
    """
    postprocess motion patch cause we preprocess motion vector to make motion video.
    """
    max_x, max_y = read_motion_vectors(motion_vector_path)
    # print(f'max_x, max_y {max_x, max_y}')
    pixel_precision = max(int(max_x) + 1, int(max_y) + 1)
    # print(f'pixel_precision {pixel_precision}')
    # print(f'patch {patch.size()} \n {patch}')
    # print(f'patch {patch.permute(1,2,0).size()} \n {patch.permute(1,2,0)}')

    h, w = patch.shape[1], patch.shape[2]  # height and width
    odd_channel_processed = patch[1, :, :].float()  # Convert to float for calculations
    even_channel_processed = patch[2, :, :].float()
    # print(odd_channel_processed)

    even_channel = (((even_channel_processed / 255.0) * 2) - 1) * pixel_precision
    even_channel = even_channel / (0.5 * w)  # Undo the scaling based on width
    odd_channel = (((odd_channel_processed / 255.0) * 2) - 1) * pixel_precision
    odd_channel = odd_channel / (0.5 * h)  # Undo the scaling based on height
    squared_sum = odd_channel ** 2 + even_channel ** 2

    sqrt_result = torch.sqrt(squared_sum)
    # print("Square root of odd^2 + even^2:\n", sqrt_result)
    average = round(sqrt_result.mean().item(), 3)
    return average




def find_motion_patch_h265(video_path, dec_fps, fps, dec_frame_number, px, py, patch_size=(64, 64)):
    """
    dec_fps: fps of decoded video
    fps: fps of reference video
    dec_frame_number: frame_number of decoded video
    """
    # video_path = f'refBMP/refOutput_166_1080_8000.mp4'
    # video_path = f'refMP4/refOutput_166_1080_8000_bistro_121_0902.mp4'
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return
    if dec_fps == fps:
        frame_ind = dec_frame_number
    else:
        frame_ind = int(safe_floor((dec_frame_number-4)/dec_fps * fps) + 2)
    # print(f'dec_frame_number {dec_frame_number}, frame_ind {frame_ind}, dec_fps {dec_fps}, fps {fps}')

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_ind)
    ret, frame = cap.read() # frame (360, 640, 3)
    if not ret: # If frame is read correctly ret is True
        print(f"Error: Could not read frame {frame_ind}")
        return None
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = torch.from_numpy(frame).permute(2, 0, 1) # 3, 360, 640
    # show_patch(frame.permute(1,2,0)) # after permute 360, 640, 3
    # print(f'frame {frame.size()}') # 1080, 1920, 3 
    patch = frame[:, py:py+patch_size[0], px:px+patch_size[1]]
    # print(f'patch {patch.permute(1,2,0).size()} \n {patch.permute(1,2,0)}')
    # show_patch(patch.permute(1,2,0))

    return patch

def read_frame_velocity(frame_velocity_path, frame_number):
    with open(frame_velocity_path, "r") as file:
        for line in file:
            frame, velocity = line.split()
            if int(frame) == frame_number:
                return float(velocity)
        return None  # Return None if frame_number is not found


def generate_patches(base_dir, path_name, motion_vector_path, motion_video_path, frame_indices, frame_velocity_path, patch_size=(64, 64), output_dir="output", scene=None):
    """
    base_dir, e.g. VRRMP4/uploaded/reference_bistro/
    bistro_path1_seg1_1/ref166_1080
    output_dir bistro_path1_seg1_1
    """
    video_path = f'{base_dir}/{path_name}/ref166_1080/refOutput.mp4'
    # print(f'video_path {video_path}')
    cap = cv2.VideoCapture(video_path)    
    if not cap.isOpened():
        print("Error opening video file")
        return 0
    frame_generated = 0
    frame_number = 0 # decoded video frame index that will be passed to find_motion_patch_h265
    while cap.isOpened(): # Read until video is completed
        if frame_number not in frame_indices:
            frame_number += 1
            more_frame = cap.grab()
            if more_frame:
                continue
            else:
                break
        ret, frame = cap.read() # frame (360, 640, 3)
        if not ret: # If frame is read correctly ret is True
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = torch.from_numpy(frame).permute(2, 0, 1) # 3, 360, 640
        # print(f'frame_number {frame_number}, frame.shape {frame.shape}')
        # show_patch(frame.permute(1,2,0)) # permute(1,2,0) gives 360, 640, 3, OpenCV reads images in BGR, so see blue-tinted image
        height, width = 1080, 1920
        interpolated_patch, px, py = get_random_patch(width, height, patch_size, frame)
        # print(f'interpolated_patch {interpolated_patch.size()}') # [3, 1080, 1080])
        if FRAME_VELOCITY:
            velocity = read_frame_velocity(frame_velocity_path, frame_number)
            # print(f'velocity {velocity}')
        if PATCH_VELOCITY:
            motion_patch = find_motion_patch_h265(motion_video_path, fps, 166, frame_number, px, py, patch_size=patch_size)
            velocity = compute_velocity(motion_patch, motion_vector_path)
            # print(f'velocity {velocity}')
            # show_patch(interpolated_patch.permute(1,2,0))
        if velocity is None:
            frame_generated += 1
            frame_number += 1
            continue

        hex_unique_id = secrets.token_hex(4)
        # path = f'{output_folder}/{hex_unique_id}_{frame_index}_{fps}_{resolution}_{bitrate}.png'
        path = f'{output_dir}/{hex_unique_id}_{int(velocity*1e5)}.png' if not FRAMENUMBER_SHOW else f'{output_dir}/{hex_unique_id}_{frame_number}_{int(velocity*1e5)}.png'
        if SAVE:
            to_pil = transforms.ToPILImage()
            interpolated_patch = to_pil(interpolated_patch)
            interpolated_patch.save(path, "png")
        frame_generated += 1
        frame_number += 1
        
        # if frame_number >= 10:
        #     break
    cap.release() # When everything done, release the video capture object
    return frame_generated


def compute_per_bitrate(fps, resolution, path_name, frame_velocity_path, total):
    frame_created_per_fps_video = 276 # frame_per_fps_video(fps) # how many frames does this fps video have
    # print(f'frame_created_per_fps_video {frame_created_per_fps_video}')
    frame_indices = [i for i in range(276)]
    count = 0 # count total number of patches generated for the fps
    patch_generated = generate_patches(base_directory, path_name, motion_vector_path, motion_video_path, \
                                    frame_indices, frame_velocity_path, output_dir=output_folder, scene=scene, patch_size=(PATCH_SIZE, PATCH_SIZE))
    print(f'{patch_generated} patches generated for resolution {resolution}p')
    count += patch_generated
    total += count
    print(f'{path_name}, {count} data')


# each id is 1 path_seg_speed, loop through all scenes given 1 id
# extract from 8000kbps bitrate only, doenst contain jod
# then run prepar_dataset_reference.py
# extract patch and patch velocity
if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('SLURM_ARRAY_TASK_ID', type=int, help='The id of task')
    # parser.add_argument('scene', type=str, help='The id of task')
    # args = parser.parse_args()
    # id = args.SLURM_ARRAY_TASK_ID
    # scene = args.scene
    # id = 1
   
    scenes = [
            # 'bedroom', 
            # 'bistro', 
            #  'crytek_sponza', 
            #  'gallery', 
            #  'living_room', 
            #  'lost_empire', 
            #  'room', 
            # 'suntemple',
            'sibenik',
            'suntemple_statue' 
            ]

    fps = 166
    resolution = 1080
    SAVE = True # True, False
    PATCH_SIZE = 64
    FRAMENUMBER_SHOW = True
    FRAME_VELOCITY = True
    PATCH_VELOCITY = False
    DROPJOD = True

    EXTRACT_PATCH = True 
    LABEL_DATA = True 
    CREATE_TRAIN_VAL_DATA = True
    CREATE_TEST_DATA = True # True, False
    
    current_date = datetime.date.today()
    output_parent_folder = f'{VRR_Patches}/{current_date}_patch{PATCH_SIZE}x{PATCH_SIZE}'
    dest_path = f'{output_parent_folder}_labeled_data'
    if CREATE_TEST_DATA:
        scenes, CREATE_TRAIN_VAL_DATA, LABEL_DATA, output_parent_folder = config_create_test_data(output_parent_folder)
    dest_path = f'{output_parent_folder}_labeled_data'
    print(f'CREATE_TRAIN_VAL_DATA {CREATE_TRAIN_VAL_DATA}')
    print(f'dest_path {dest_path}')

    if EXTRACT_PATCH:
        for scene in scenes:
            print(f'====================== scene {scene} ======================')
            for id in range(1, 46): # 46
                id -= 1
                path, seg, speed = mapIdToPath(id)
                # print(f'{scene} path, seg, speed {path, seg, speed}')
                base_directory = f'{VRRMP4_reference}/{scene}'
                current_date = datetime.date.today()
                output_folder = f'{output_parent_folder}/reference_{scene}/{scene}_path{path}_seg{seg}_{speed}'
                frame_velocity_path = f'{VRR_Motion}/reference/magnitude_motion_per_frame/{scene}/{scene}_path{path}_seg{seg}_{speed}_velocity_per_frame.txt'
                os.makedirs(output_folder, exist_ok=True)

                path_name = f'{scene}_path{path}_seg{seg}_{speed}'

                total = 0
                motion_vector_path = f'{VRR_Motion}/reference/motion_vector_reference/{scene}/{scene}_path{path}_seg{seg}_{speed}_velocity_cleaned.txt'
                motion_video_path = f'{VRR_Motion}/reference/refMP4_reference/{scene}/{scene}_path{path}_seg{seg}_{speed}_refOutput_166_1080_8000.mp4'
                compute_per_bitrate(fps, resolution, path_name, frame_velocity_path, total)
    
    if LABEL_DATA:
        bitrates = [500, 1000, 1500, 2000]
        COPY = True # False True

        # scene_velocity_dicts = {'suntemple_statue': bistro_max_comb_per_sequence}
        for scene in scenes:
            if not os.path.exists(output_parent_folder):
                print(f"Folder '{output_parent_folder}' does not exist. Exiting...")
                exit()  # Stop the script execution
                
            scene_dir = f'{output_parent_folder}/reference_{scene}'
            if DROPJOD:
                velocity_dict = drop_JOD_dicts[scene]
            else:
                velocity_dict = scene_velocity_dicts[scene] # scene_velocity_dicts[scene] dropJOD
            rename_subfolders_for_scene(scene, velocity_dict, scene_dir, bitrates, dest_path, MOVE=COPY, FRAMENUMBER_SHOW=FRAMENUMBER_SHOW)
        print(f'\nLabeled data are saved to {dest_path}\n')

    if CREATE_TRAIN_VAL_DATA:
        # in place move
        create_train_validation_data(dest_path)

    print(f'DROPJOD {DROPJOD}')
