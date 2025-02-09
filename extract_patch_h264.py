import cv2
import numpy as np
import os
import gc
import secrets
from utils_windows import *
from utils_windows import *
import datetime
import argparse
import torch
import torchvision.transforms as transforms
from memory_profiler import profile




def get_patch_by_grid(width, height, patch_size, frame):
    # Generate patches by dividing frame to 64x64 grids
    for i in range(0, height, patch_size[0]):
        for j in range(0, width, patch_size[1]):
            # Ensure the patch does not go out of frame boundaries
            if (i + patch_size[0] <= height) and (j + patch_size[1] <= width):
                # print(f'i, j {i, j}')
                patch = frame[i:i+patch_size[0], j:j+patch_size[1]]
                # show_patch(patch)

                # Save or process the patch here
                # cv2.imwrite(f'{output_folder}/patch_{frame_index}_{i}_{j}.png', patch)
            break


def get_random_patch(width, height, patch_size, interpolated_img):
    max_x = width - patch_size[1]
    max_y = height - patch_size[0]
    x = np.random.randint(0, max_x + 1) # TODO
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
    max_x, max_y = read_motion_vectors(motion_vector_path)
    # print(f'max_x, max_y {max_x, max_y}')
    pixel_precision = max(int(max_x) + 1, int(max_y) + 1)
    # print(f'pixel_precision {pixel_precision}')
    # print(f'patch {patch.size()} \n {patch}')
    # print(f'patch {patch.permute(1,2,0).size()} \n {patch.permute(1,2,0)}')

    h, w = patch.shape[1], patch.shape[2]  # height and width
    # print(h, w)
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
    
    frame_ind = int(safe_floor((dec_frame_number-4)/dec_fps * fps) + 2)
    # print(f'dec_frame_number {dec_frame_number}, dec_fps {dec_fps}, fps {fps}')

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


def generate_patches(base_dir, bitrate, fps, resolution, motion_vector_path, motion_video_path, frame_indices, rounds=1, patch_size=(64, 64), output_dir="output", scene=None):
    """
    base_dir, e.g. VRRMP4_CVVDP/bistro/bistro_path1_seg1_1
    """
    output_png_dir = os.path.join(output_dir, f'{bitrate}kbps') 
    os.makedirs(output_png_dir, exist_ok=True)
       
    specs = f'{fps}_{resolution}_{bitrate}'
    fps_dir = os.path.join(base_dir, f'{bitrate}kbps', f'fps{fps}', specs) # h264 inside the dir
    files = os.listdir(fps_dir)
    video_path = os.path.join(fps_dir, files[0])
    # print(f'files {files}')
    # print(f'video_path {video_path}')
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error opening video file")
        return
    
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
        # print(f'frame_number {frame_number}')
        ret, frame = cap.read() # frame (360, 640, 3)
        if not ret: # If frame is read correctly ret is True
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = torch.from_numpy(frame).permute(2, 0, 1) # 3, 360, 640
        # print(f'frame.shape {frame.shape}')
        # show_patch(frame.permute(1,2,0)) # permute(1,2,0) gives 360, 640, 3, OpenCV reads images in BGR, so see blue-tinted image
        height, width = 1080, 1920
        interpolated_img = torch.nn.functional.interpolate(frame.unsqueeze(0), size=(height, width), mode='bicubic').squeeze(0)
        # print(f'interpolated_img {interpolated_img.size()} {interpolated_img.permute(1,2,0).size()}')
        # show_patch(interpolated_img.permute(1,2,0))
        # print(f'======================= frame_number {frame_number} =======================') # 1 frame generate number of rounds patches
        for _ in range(rounds): # rounds is always 1 here
            interpolated_patch, px, py = get_random_patch(width, height, patch_size, interpolated_img)
            # print(f'interpolated_patch {interpolated_patch.size()}') # [3, 1080, 1080])
            # print(f'px py {px, py}')
            # show_patch(interpolated_patch.permute(1,2,0))

            motion_patch = find_motion_patch_h265(motion_video_path, fps, 166, frame_number, px, py, patch_size=(64, 64))
            velocity = compute_velocity(motion_patch, motion_vector_path)
            # print(f'velocity {velocity}')

            hex_unique_id = secrets.token_hex(4)
            # path = f'{output_folder}/{hex_unique_id}_{frame_index}_{fps}_{resolution}_{bitrate}.png'
            path = f'{output_png_dir}/{hex_unique_id}_{fps}_{resolution}_{bitrate}_{int(velocity*1000)}.png'
            if SAVE:
                to_pil = transforms.ToPILImage()
                interpolated_patch = to_pil(interpolated_patch)
                interpolated_patch.save(path, "png")
            frame_generated += 1
            
        # del frame
        # del interpolated_img
        # gc.collect()
        # show_patch(patch)
        frame_number += 1
        
        # if frame_number >= 10:
        #     break
    cap.release() # When everything done, release the video capture object
    return frame_generated


def compute_per_bitrate(bitrates, fps_arr, total):
    for bitrate in bitrates: 
        print(f'====================== bitrate {bitrate} ======================')
        for fps in fps_arr: 
            print(f'====================== fps {fps} ======================')
            frame_created_per_fps_video = frame_per_fps_video(fps) # how many frames does this fps video have
            frame_indices = np.random.choice(frame_created_per_fps_video, frame_save_per_video, replace=False)
            frame_indices.sort()
            # print(f'frame_indices {frame_indices}')
            # print(f'frame_limit_per_fps_video {frame_created_per_fps_video}')
            rounds = int(frame_save_per_video/frame_created_per_fps_video) # how many patches do we generate per frame, make sure different fps has same number of patches
            rounds = max(1, rounds)
            # print(f'rounds {rounds}')
            count = 0 # count total number of patches generated for the fps
            for resolution in resolution_arr:
                    # print(f'resolution {resolution}') 
                    patch_generated = generate_patches(base_directory, bitrate, fps, resolution, motion_vector_path, motion_video_path, \
                                                    frame_indices, rounds=rounds, output_dir=output_folder, scene=scene, patch_size=(64, 64))
                    # print(f'{patch_generated} patches generated for resolution {resolution}p')
                    count += patch_generated
            total += count
            print(f'{count} data generated for fps {fps}')
    print(f'{total} data generated for {len(bitrates)} bitrates, {len(fps_arr)} fps and {len(resolution_arr)} resolutions.')


# each id is 1 path_seg_speed, loop through all scenes given 1 id
if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('SLURM_ARRAY_TASK_ID', type=int, help='The id of task')
    # args = parser.parse_args()
    # id = args.SLURM_ARRAY_TASK_ID
    # id = 3

    # scene_arr = ["bistro"] # full list are in utils.py
    resolution_arr = [360, 480, 720, 864, 1080]
    # resolution_arr = [360]
    bitrates = [500, 1000, 1500, 2000,]
    # bitrates = [2000]
    fps_arr = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120,]
    # fps_arr = [120,]
    SAVE = True # True, False
    for id in range(35, 46):
        id -= 1
        path, seg, speed = mapIdToPath(id)
        print(f'id {id}, path, seg, speed {path, seg, speed}')

        # scene_arr = ['bistro'] # TODO
        frame_save_per_video = 50 # fps 120 has 200 frames in 1 video, framelimit - fps is number of frames per video
        NUM_PATCH_REQUIRED = frame_save_per_video * len(resolution_arr) # 665, each bistrate, fps, path_seg_speed 
        print(f'NUM_PATCH_REQUIRED {NUM_PATCH_REQUIRED}')
        
        scene_arr = ['suntemple_statue']
        scene = scene_arr[0]
        # for scene in scene_arr:
        print(f'====================== scene {scene} ======================')
        base_directory = f'{VRRMP4_CVVDP}/{scene}/{scene}_path{path}_seg{seg}_{speed}'
        current_date = datetime.date.today()
        output_folder = f'{VRR_Patches}/{current_date}/{scene}/{scene}_path{path}_seg{seg}_{speed}'
        os.makedirs(output_folder, exist_ok=True)

        total = 0

        motion_vector_path = f'{VRR_Motion}/reference/motion_vector_reference/{scene}/{scene}_path{path}_seg{seg}_{speed}_velocity_cleaned.txt'
        motion_video_path = f'{VRR_Motion}/reference/refMP4_reference/{scene}/{scene}_path{path}_seg{seg}_{speed}_refOutput_166_1080_8000.mp4'
        # bistro_path1_seg1_1\500kbps should have NUM_PATCH_REQUIRED * len(fps)
        compute_per_bitrate(bitrates, fps_arr, total)
