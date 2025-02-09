import cv2
import numpy as np
import os
import secrets
import imageio
from utils import *
from PIL import Image
import matplotlib.pyplot as plt
from utils import *
import datetime
import random
import torch
import torchvision.transforms as transforms

import os

motion_folder = r"C:\Users\15142\Projects\VRR\VRR_Motion\motion"  # Change to your actual folder path
global_min = float('inf')
# global_max = float('-inf')

# Loop through all subdirectories and files
for root, _, files in os.walk(motion_folder):
    for file in files:
        if file.endswith(".dat"):  # Process only .dat files
            file_path = os.path.join(root, file)
            try:
                data = np.fromfile(file_path, dtype=np.float32)  # Read binary float32 data
                if data.size > 0:  # Ensure file is not empty
                    # file_min, file_max = data.min(), data.max()
                    velocity = np.sqrt(data[0]**2 + data[1]**2)
                    global_min = min(global_min, velocity)
                    # print(f"Processed: {file_path}, velocity: {velocity}, global_min: {global_min}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

print(f"\nGlobal Min: {global_min}"



# patch = torch.tensor([[[  0,   0,   0,   0,   0,   0,   0,   0],
#          [  0,   0,   0,   0,   0,   0,   0,   0],
#          [  0,   0,   0,   0,   0,   0,   0,   0],
#          [  0,   0,   0,   0,   0,   0,   0,   0],
#          [  0,   0,   0,   0,   0,   0,   0,   0],
#          [  0,   0,   0,   0,   0,   0,   0,   0],
#          [  0,   0,   0,   0,   0,   0,   0,   0],
#          [  0,   0,   0,   0,   0,   0,   0,   0]],

#         [[154, 154, 154, 154, 154, 154, 154, 154],
#          [154, 154, 154, 154, 154, 154, 154, 154],
#          [154, 154, 154, 154, 154, 154, 154, 154],
#          [154, 154, 154, 154, 154, 154, 154, 154],
#          [154, 154, 154, 154, 154, 154, 154, 154],
#          [154, 154, 154, 154, 154, 154, 154, 154],
#          [154, 154, 154, 154, 154, 154, 154, 154],
#          [154, 154, 154, 154, 154, 154, 154, 154]],

#         [[184, 184, 184, 184, 184, 184, 184, 184],
#          [184, 184, 184, 184, 184, 184, 184, 184],
#          [184, 184, 184, 184, 184, 184, 184, 184],
#          [184, 184, 184, 184, 184, 184, 184, 184],
#          [184, 184, 184, 184, 184, 184, 184, 184],
#          [184, 184, 184, 184, 184, 184, 184, 184],
#          [184, 184, 184, 184, 184, 184, 184, 184],
#          [184, 184, 184, 184, 184, 184, 184, 184]]])

# h, w = patch.shape[1], patch.shape[2]  # height and width

# blue_channel = patch[0, :, :]
# odd_channel_processed = patch[1, :, :].float()  # Convert to float for calculations
# even_channel_processed = patch[2, :, :].float()
# # print(odd_channel_processed)

# pixel_precision = 3
# even_channel = (((even_channel_processed / 255.0) * 2) - 1) * pixel_precision
# even_channel = even_channel / (0.5 * w)  # Undo the scaling based on width

# # Undo the transformations for odd channel
# odd_channel = (((odd_channel_processed / 255.0) * 2) - 1) * pixel_precision
# odd_channel = odd_channel / (0.5 * h)  # Undo the scaling based on height

# print(f'even_channel \n {even_channel}')
# print(f'odd_channel \n {odd_channel}')
# print(even_channel**2)
# print(odd_channel**2)

# squared_sum = odd_channel ** 2 + even_channel ** 2

# # Compute the square root of the sum
# # print(f'squared_sum \n {squared_sum}')

# sqrt_result = torch.sqrt(squared_sum)

# print("Square root of odd^2 + even^2:\n", sqrt_result)
# total_sum = sqrt_result.sum()

# # Take the average of sqrt_result
# average = sqrt_result.mean()

# print("Sum of sqrt_result:", total_sum.item())
# print("Average of sqrt_result:", average.item())

# fps_arr = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120,]
# numOfFrames = 50
# for frameRate in fps_arr: 
#     frameLimit = frameRate + numOfFrames * frameRate / 30.0
    # print(f'frameRate {frameRate}, frameLimit {frameLimit}')

# frame_limit_per_fps()
# frame_indices = np.random.choice(200, 50, replace=False)
# frame_indices.sort()  # Sort the indices to sample in order
# print(frame_indices)
# print(3 in frame_indices)
# path, seg, speed = mapIdToPath(44)
# print(path, seg, speed)

# import os
# scene_arr = ['bedroom', 'bistro', 'crytek_sponza', 'gallery', 'living_room', 'lost_empire', 'room', 'sibenik', 'suntemple', 'suntemple_statue']
# for scene in scene_arr:
#     path = f'/home/yl962/rds/hpc-work/VRR/logs/vrr_patches/{scene}'
#     os.makedirs(path, exist_ok=True)
#     print(f'{path} is created.')
# path = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\2024-09-12\suntemple_statue\suntemple_statue_path4_seg2_1\2000kbps'
# path = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\HPC\2024-09-11\bedroom\bedroom_path1_seg1_3\2000kbps'
# print(f'number of files: {count_files(path)}')

# id = mapPathToId(2, 2, 3)
# print(id)

# fps_column = torch.tensor([ 80.,  90.,  50.,  ..., 100., 100., 120.])
# resolution_column = torch.tensor([1080.,  720.,  720.,  ...,  720.,  864.,  360.])
# fps_keys = torch.tensor([ 30,  40,  50,  60,  70,  80,  90, 100, 110, 120])
# res_keys = torch.tensor([ 360,  480,  720,  864, 1080])
# fps_indices = torch.tensor([1, 1, 1,  ..., 2, 2, 2])
# res_indices = torch.tensor([4, 4, 4,  ..., 2, 2, 2])

def normalize_column(column, data):
    mean = np.mean(data)
    std_dev = np.std(data)
    return (column - mean) / std_dev



# resolutions = torch.tensor([360, 1080, 720, 480, 864])
# resolution_data = [360, 480, 720, 864, 1080]

# # Mapping dictionary
# res_map = {360: 0, 480: 1, 720: 2, 864: 3, 1080: 4}
# # Create a list of corresponding indices using the res_map
# mapped_indices = torch.tensor([res_map[res.item()] for res in resolutions])

# # Print the result
# print(f'mapped_indices \n {mapped_indices}')

# normalized_res_column = normalize_column(resolutions, resolution_data)
# print(f'normalized_res_column \n {normalized_res_column}')


# res_keys = torch.tensor(list(res_map.keys()))  # Tensor of resolution values
# res_values = torch.tensor(list(res_map.values()))  # Tensor of corresponding indices
# print(f'res_keys {res_keys}')
# print(f'res_values {res_values}')

# # Use torch.searchsorted to find the index in res_keys for each resolution
# indices = torch.searchsorted(res_keys, resolutions)
# print(f'indices {indices}')

# # Map the found indices to their corresponding values in res_values
# mapped_indice = res_values[indices]
# print(f'mapped_indices {mapped_indice}')

# max_x, max_y = read_motion_vectors(motion_vector_path)
# print(f'max_x, max_y {max_x, max_y}')
# max_x, max_y = (1701295232.0, 821091392.0)
# pixel_precision = max(int(max_x) + 1, int(max_y) + 1)
# print(f'pixel_precision {pixel_precision}')
# print(f'patch {patch.size()} \n {patch}')
# print(f'patch {patch.permute(1,2,0).size()} \n {patch.permute(1,2,0)}')

# h, w = patch.shape[1], patch.shape[2]  # height and width
# # print(h, w)
# odd_channel_processed = 127 # Convert to float for calculations
# even_channel_processed = 127
# # print(odd_channel_processed)

# even_channel = (((even_channel_processed / 255.0) * 2) - 1) * pixel_precision
# even_channel = even_channel / (0.5 * w)  # Undo the scaling based on width
# odd_channel = (((odd_channel_processed / 255.0) * 2) - 1) * pixel_precision
# odd_channel = odd_channel / (0.5 * h)  # Undo the scaling based on height
# squared_sum = odd_channel ** 2 + even_channel ** 2

# sqrt_result = np.sqrt(squared_sum)
# # print("Square root of odd^2 + even^2:\n", sqrt_result)
# average = round(sqrt_result.mean().item(), 3)
# # print(f'average {average}')

# fps = torch.tensor([0.2220, 0.6670, 0.7780], device='cuda:0', dtype=torch.float64)
# resolution = torch.tensor([0.5000, 0.0000, 0.1670], device='cuda:0', dtype=torch.float64)
# bitrate = torch.tensor([1.0000, 0.6670, 0.6670], device='cuda:0', dtype=torch.float64)
# velocity = torch.tensor([-0.0930, -0.0930, -0.0930], device='cuda:0', dtype=torch.float64)

# fps_resolution_bitrate = torch.stack([fps, resolution, bitrate, velocity], dim=1).float()

# # print(f'frame_indices {frame_indices}')
# from find_JOD_loss import get_jod_score
# from JOD import crytek_sponza_jod
# # all_data = {'path3_seg3_2': {500: {30: {'360': 5.2487, '480': 5.2084, '720': 5.0423, '864': 4.8606, '1080': 4.7056}, 40: {'360': 5.7435, '480': 5.7615, '720': 5.6516, '864': 5.4425, '1080': 5.2399}, 50: {'360': 6.0169, '480': 6.0691, '720': 5.9798, '864': 5.7311, '1080': 5.5531}, 60: {'360': 6.1186, '480': 6.1793, '720': 6.1094, '864': 5.922, '1080': 5.6505}, 70: {'360': 6.1942, '480': 6.2552, '720': 6.2082, '864': 6.0506, '1080': 5.7107}, 80: {'360': 6.287, '480': 6.3629, '720': 6.3139, '864': 6.1805, '1080': 5.0917}, 90: {'360': 6.301, '480': 6.3875, '720': 6.3327, '864': 6.2231, '1080': 4.4945}, 100: {'360': 6.3056, '480': 6.377, '720': 6.355, '864': 6.2507, '1080': 3.9627}, 110: {'360': 6.32, '480': 6.4089, '720': 6.3673, '864': 6.2809, '1080': 3.8352}, 120: {'360': 6.3266, '480': 6.4079, '720': 6.3839, '864': 6.1794, '1080': 3.8857}}}}
# print(get_jod_score(crytek_sponza_jod, 'path1_seg2_1', 1500, 50, '720'))


# generate a patch from bistro path1 seg1 1
def get_random_patch(width, height, patch_size, interpolated_img):
    max_x = width - patch_size[1]
    max_y = height - patch_size[0]
    x = np.random.randint(0, max_x + 1) 
    y = np.random.randint(0, max_y + 1)
    # print(f'x, y {x, y}')

    interpolated_patch = interpolated_img[:, y:y+patch_size[0], x:x+patch_size[1]]
    return interpolated_patch, x, y

def generate_patches(frame_indices, patch_size=(128, 128), output_dir="output"):
    """
    base_dir, e.g. VRRMP4/uploaded/reference_bistro/
    bistro_path1_seg1_1/ref166_1080
    output_dir bistro_path1_seg1_1
    """
    base = r'C:\Users\15142\Projects\VRR\VRRMP4\uploaded\reference\reference_bistro\bistro_path1_seg1_1'
    video_path = f'{base}/ref166_1080/refOutput.mp4'
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
        # print(f'velocity {velocity}')
        # show_patch(interpolated_patch.permute(1,2,0))

        hex_unique_id = secrets.token_hex(4)
        # path = f'{output_folder}/{hex_unique_id}_{frame_index}_{fps}_{resolution}_{bitrate}.png'
        path = f'{hex_unique_id}_{frame_number}.png'
        if True:
            to_pil = transforms.ToPILImage()
            interpolated_patch = to_pil(interpolated_patch)
            interpolated_patch.save(path, "png")
        frame_generated += 1
        frame_number += 1

    cap.release() # When everything done, release the video capture object
    return frame_generated
# generate_patches([1, 3, 5, 10, 15, 16], output_dir="output")