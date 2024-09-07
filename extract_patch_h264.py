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



def get_patch_by_grid(width, height, patch_size, frame):
    # Generate patches by dividing frame to 64x64 grids
    for i in range(0, height, patch_size[0]):
        for j in range(0, width, patch_size[1]):
            # Ensure the patch does not go out of frame boundaries
            if (i + patch_size[0] <= height) and (j + patch_size[1] <= width):
                # print(f'i, j {i, j}')
                patch = frame[i:i+patch_size[0], j:j+patch_size[1]]
                show_patch(patch)

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
    print(f'max_x, max_y {max_x, max_y}')
    pixel_precision = max(int(max_x) + 1, int(max_y) + 1)
    print(f'pixel_precision {pixel_precision}')
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
    average = sqrt_result.mean()

    return round(average.item(), 3)




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
    print(f'dec_frame_number {dec_frame_number}, dec_fps {dec_fps}, fps {fps}')

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_ind)
    ret, frame = cap.read() # frame (360, 640, 3)

    if not ret: # If frame is read correctly ret is True
        print(f"Error: Could not read frame {frame_ind}")
        return None

    frame = torch.from_numpy(frame).permute(2, 0, 1) # 3, 360, 640
    # show_patch(frame.permute(1,2,0)) # after permute 360, 640, 3
    print(f'frame {frame.permute(1,2,0).size()}') # 1080, 1920, 3 
    patch = frame[:, py:py+patch_size[0], px:px+patch_size[1]]
    # print(f'patch {patch.permute(1,2,0).size()} \n {patch.permute(1,2,0)}')
    # show_patch(patch.permute(1,2,0))

    return patch



def generate_patches(base_dir, bitrate, fps, resolution, motion_vector_path, motion_video_path, count, rounds=1, patch_size=(64, 64), output_dir="output", scene=None):
    """
    base_dir, e.g. VRRMP4_CVVDP/bistro/bistro_path1_seg1_1
    """
    output_png_dir = os.path.join(output_dir, f'{bitrate}kbps') 
    os.makedirs(output_png_dir, exist_ok=True)
       
    specs = f'{fps}_{resolution}_{bitrate}'
    fps_dir = os.path.join(base_dir, f'{bitrate}kbps', f'fps{fps}', specs) # h264 inside the dir
    files = os.listdir(fps_dir)
    video_path = os.path.join(fps_dir, files[0])
    print(f'files {files}')
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error opening video file")
        return
    
    frame_generated = 0

    frame_number = 0
    while cap.isOpened(): # Read until video is completed
        # if count + frame_generated >= NUM_PATCH_REQUIRED:
        #     break
        ret, frame = cap.read() # frame (360, 640, 3)
        if not ret: # If frame is read correctly ret is True
            break
        
        frame = torch.from_numpy(frame).permute(2, 0, 1) # 3, 360, 640
        print(f'frame.shape {frame.shape}')
        # show_patch(frame.permute(1,2,0)) # after permute 360, 640, 3
        # height, width, _ = frame.shape
        height, width = 1080, 1920
        interpolated_img = torch.nn.functional.interpolate(frame.unsqueeze(0), size=(height, width), mode='bicubic').squeeze(0)
        print(f'interpolated_img {interpolated_img.size()} {interpolated_img.permute(1,2,0).size()}')
        
        # show_patch(interpolated_img.permute(1,2,0))
        for _ in range(rounds):
            # if count >= NUM_PATCH_REQUIRED:
            #         break
            interpolated_patch, px, py = get_random_patch(width, height, patch_size, interpolated_img)
            print(f'interpolated_patch {interpolated_patch.size()}') # [3, 1080, 1080])
            print(f'px py {px, py}')
            # show_patch(interpolated_patch.permute(1,2,0))

            motion_patch = find_motion_patch_h265(motion_video_path, fps, 166, frame_number, px, py, patch_size=(64, 64))

            velocity = compute_velocity(motion_patch, motion_vector_path)
            print(f'velocity {velocity}')

            hex_unique_id = secrets.token_hex(4)
            # path = f'{output_folder}/{hex_unique_id}_{frame_index}_{fps}_{resolution}_{bitrate}.png'
            # path = f'{output_dir}/{hex_unique_id}_{fps}_{resolution}_{bitrate}.png'
            # if scene:
            #     path = f'{output_png_dir}/{hex_unique_id}_{fps}_{resolution}_{bitrate}_x{scene}.png'
            # else:
            path = f'{output_png_dir}/{hex_unique_id}_{fps}_{resolution}_{bitrate}_{int(velocity*1000)}.png'
            if SAVE:
                to_pil = transforms.ToPILImage()
                interpolated_patch = to_pil(interpolated_patch)
                interpolated_patch.save(path, "png")
            # count += 1
            frame_generated += 1

        # show_patch(patch)
        # frame_index += 1

    # cap.release() # When everything done, release the video capture object
    # # print(f"Processing completed. {frame_generated} generated for resolution {resolution}")
        frame_number += 1
        if frame_number >= 10:
            break
    return frame_generated




if __name__ == "__main__":
    id = 1
    # scene can be passed

    # base_path = f'C:/Users/15142/new/Falcor/Source/Samples/EncodeDecode/encodedH264/data'
    # scene_arr = ['bistro_glasses2', 'bistropath_one1', ]
    scene_arr = ['bistropath_one1', 'bistropath_one2', 'bistropath_three1', 'bistropath_three2', 'bistro_glasses2', \
                 'breakfast_room_two1', 'lost_empire_three1',  'sponza_three1', \
                  'paint2', 'room1', 'room2', \
                  'suntemple1', 'suntemple2', 
                #   'suntemple_statue2'
                  ]
    scene_arr = ["bistro"]
    resolution_arr = [360, 480, 720, 864, 1080]
    resolution_arr = [360]
    bitrates = [500, 1000, 1500, 2000,]
    bitrates = [500]
    fps_arr = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120,]
    fps_arr = [30,]
    SAVE = True # True, False

    id -= 1
    path, seg, speed = mapIdToPath(id)
    print(f'path, seg, speed {path, seg, speed}')
    for scene in scene_arr:
        print(f'====================== scene {scene} ======================')

        base_directory = f'{VRRMP4_CVVDP}/{scene}/{scene}_path{path}_seg{seg}_{speed}'
        current_date = datetime.date.today()
        output_folder = f'{VRR_Patches}/{current_date}/{scene}/{scene}_path{path}_seg{seg}_{speed}'
        os.makedirs(output_folder, exist_ok=True)

        total = 0
        # NUM_PATCH_REQUIRED = 120 * len(fps_arr) * len(bitrates) # 665
        # for each fps, 120 * len(resolution_arr) patches 
        NUM_PATCH_REQUIRED = 120 * len(resolution_arr) 

        # print(f'NUM_PATCH_REQUIRED {NUM_PATCH_REQUIRED}')

        motion_vector_path = f'{VRR_Motion}/motion_vector/{scene}/{scene}_path{path}_seg{seg}_{speed}_velocity_cleaned.txt'
        motion_video_path = f'{VRR_Motion}/refMP4/{scene}/{scene}_path{path}_seg{seg}_{speed}_refOutput_166_1080_8000.mp4'
        for bitrate in bitrates: # 120 * len(fps_arr) patches for each bitrate
            print(f'====================== bitrate {bitrate} ======================')
            for fps in fps_arr: # for each fps, save 120 patches for each resolution
                print(f'====================== fps {fps} ======================')

                # rounds = int(120/fps) # make sure different fps has same number of patches
                rounds = 1
                # print(f'rounds {rounds}')
                count = 0 # count total number of patches generated for the fps
                for resolution in resolution_arr: # 120 patches saved for each resolution
                        count += generate_patches(base_directory, bitrate, fps, resolution, motion_vector_path, motion_video_path, \
                                                        count, rounds=rounds, output_dir=output_folder, scene=scene, patch_size=(64, 64))
                        # total += count
                # # print(f'for loop {count} for {len(resolution_arr)} resolution')
                # # for resolution in [360, 480, 720, 864, 1080]:
                # # print(f'=================== while loop ===================')
                # while True:
                #     if count >= NUM_PATCH_REQUIRED:
                #             break
                    
                #     random_resolution = random.choice(resolution_arr)
                #     # print(f'random resolution {random_resolution}')
                #     # for resolution in resolution_arr:
                #     count += generate_patches(base_directory, bitrate, fps, random_resolution, \
                #                                     count, output_dir=output_folder)
                #     # print(f'after resolution {resolution}, count {count}')
                # total += count
                # # print(f'{count} data generated for fps {fps}')
        print(f'{total} data generated for {len(bitrates)} bitrates, {len(fps_arr)} fps and {len(resolution_arr)} resolutions.')



        # generate_patches(video_path, output_folder)
