import os
import numpy as np
import math
from PIL import Image
from utils import *
import torch
import torchvision.transforms as transforms
import datetime
import secrets
from natsort import natsorted



def extract_patches(base_dir, bitrate, fps, resolution, count, rounds=1, output_dir="", patch_size=(64, 64)): # patch size height, width

    output_png_dir = os.path.join(output_dir, f'{bitrate}kbps') # e.g. 60_360_2000
    os.makedirs(output_png_dir, exist_ok=True)

    fps_dir = os.path.join(base_dir, f'{bitrate}bps', f'fps{fps}', f'{fps}_{resolution}_{bitrate}')
    files = [os.path.join(fps_dir, f) for f in os.listdir(fps_dir) if f.endswith(('bmp'))]
    files = natsorted(files)  # Ensure the files are in some order
    # print(f'files {files}')
    if len(files) < 3:
        print("Error: Not enough images in the directory.")
        return
    
    image_height, image_width = 1080, 1920
    max_x = image_width - patch_size[1]
    max_y = image_height - patch_size[0]   
    
    # print(f'files {files}\n')
    for j in range(len(files) - 2):
        for _ in range(rounds):
            if count >= NUM_PATCH_REQUIRED:
                break
            count += 1
            x = np.random.randint(0, max_x + 1)
            y = np.random.randint(0, max_y + 1)
            patches = []
            for i in range(3):
                # print(f'i {i}, i+j {i+j}')
                test_img = Image.open(files[i+j]).convert('RGB')
                transform = transforms.ToTensor()
                test_img = transform(test_img)

                test_img = torch.nn.functional.interpolate(test_img.unsqueeze(0), size=(image_height, image_width), mode='bicubic').squeeze(0)
                # show_patch(test_img.permute(1,2,0))

                test_patch = test_img[:, y:y+patch_size[0], x:x+patch_size[1]]
                
                test_patch = torch.clamp(test_patch, min=0, max=1)
                # print(f'test_patch {test_patch.size(), test_patch.max(), test_patch.min()}')
                # print(f'ref_patch {ref_patch.size(), ref_patch.max(), ref_patch.min()}')
                patches.append(test_patch)
                # show_patch(test_patch.permute(1,2,0))
            concatenated_patches = torch.cat(patches, dim=2)  # dim=2 for width
            # print(f'concatenated_patches {concatenated_patches}')


            to_pil = transforms.ToPILImage()
            concatenated_patches = to_pil(concatenated_patches)
            # show_patch(concatenated_patches)

            # print(f'concatenated_patches {concatenated_patches}')
            hex_unique_id = secrets.token_hex(4)
            path = os.path.join(f'{output_png_dir}', f'{hex_unique_id}_{fps}_{resolution}_{bitrate}.png')
            # print(f'path {path}')
            concatenated_patches.save(path, "png")
            # print(f'save concatenated patches')
    return count


if __name__ == "__main__":
    # base_directory = 'C:/Users/15142/Desktop/VRR/VRR_Frames/suntemple-fast'
    base_directory = 'D:/VRR-frame/suntemple-fast'
    # base_directory = 'C:/Users/15142/Desktop/VRR/VRR_Frames/bistro-fast'
    output_directory = 'C:/Users/15142/Desktop/VRR/VRR_Patches/suntemple-fast/'
    # Train_Dir = 'C:/Users/15142/Desktop/VRR/VRR_Patches/bistro-normal'


    resolution_arr = [360, 480, 720, 864, 1080]
    # resolution_arr = [360]
    # bitrates = [2000, 3000]
    bitrates = [3500, 5000, 7500]
    # bitrate = 2000
    fps_arr = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120,]
    # fps_arr = [30]

    current_date = datetime.date.today()
    output_dir = f'{output_directory}/{current_date}/consecutive_dec'

    total = 0
    NUM_PATCH_REQUIRED = 580 # fps 120 generate 580 patches if go through once
    for bitrate in bitrates:
        print(f'====================== bitrate {bitrate} ======================')
        for fps in fps_arr:
            rounds = int(np.ceil(116/fps)) # make sure different fps has same number of patches
            count = 0 # count total number of patches generated for the fps
            for resolution in resolution_arr:
                    count = extract_patches(base_directory, bitrate, fps, resolution, \
                                                    count, rounds=rounds, output_dir=output_dir)

            
            while True:
                if count >= NUM_PATCH_REQUIRED:
                        break
                for resolution in resolution_arr:
                    count = extract_patches(base_directory, bitrate, fps, resolution, count, output_dir=output_dir)
            total += count
            print(f'{count} data generated for fps {fps}')
    print(f'{total} data generated.')


