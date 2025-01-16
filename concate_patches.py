import os
import numpy as np
import math
from PIL import Image
from utils import *
import torch
import torchvision.transforms as transforms
import datetime
import secrets


# patch = (h, w)
def extract_and_concatenate(base_dir, bitrate, fps, resolution, count, rounds=1, patch_size=(64, 64), \
                            output_dir="output", motion_dir="", VELOCITY=False):
    # print(f'extract function count {count}')
    # output_png_dir = os.path.join(output_dir, f'{bitrate}bps', f'fps{fps}', f'{fps}_{resolution}_{bitrate}') # e.g. 60_360_2000
    output_png_dir = os.path.join(output_dir, f'{bitrate}bps') 
    # print(f'output_dir {output_dir}')    
    specs = f'{fps}_{resolution}_{bitrate}'
    fps_dir = os.path.join(base_dir, f'{bitrate}bps', f'fps{fps}', specs)
    # print(f'fps_dir {fps_dir}')
    ref_dir = os.path.join(f'{base_dir}', f"ref160_1080")
    # print(f'ref_dir {ref_dir}\n\n\n')

    os.makedirs(output_png_dir, exist_ok=True)

    # Iterate through each BMP file in the fps/resolution directory
    for filename in os.listdir(fps_dir):
        if count >= NUM_PATCH_REQUIRED:
            # print(f'break')
            break
        # print(f'filename {filename} {count}')

        if filename.endswith(".bmp") and not os.path.isdir(os.path.join(fps_dir, filename)):
            test_img_path = os.path.join(fps_dir, filename)
            number = int(filename.split('.')[0])

            frame_ind = int(safe_floor((number-4)/fps * 160) + 2)
            
            # print(f'number, frame_ind {number, frame_ind}')
            ref_img_path = os.path.join(ref_dir, f"{frame_ind}.bmp")  # Assuming 'x.bmp' is a placeholder
            # print(f'ref_img_path {ref_img_path}\n')       
            test_img = Image.open(test_img_path).convert('RGB')
            ref_img = Image.open(ref_img_path).convert('RGB')
            transform = transforms.ToTensor()
            test_img = transform(test_img)
            ref_img = transform(ref_img)
        
            # show_patch(test_img.permute(1,2,0))
            # show_patch(ref_img.permute(1,2,0))

            _, image_height, image_width = ref_img.size()      



            # find velocity
            velocity = 0
            if VELOCITY:
                motion_path = f'{motion_dir}/motion_{specs}.txt'
                # print(f'motion_path {motion_path}')
                frame_num = filename.replace('.bmp', '') 
                # print(f'filename {filename}, frame_num {frame_num}')
                velocity = get_frame_value(motion_path, frame_num)
                # print(f'velocity {velocity} {type(velocity)}')
                velocity = float(velocity) * 10000
                velocity = int(velocity)

            test_img = torch.nn.functional.interpolate(test_img.unsqueeze(0), size=(image_height, image_width), mode='bicubic').squeeze(0)
            max_x = image_width - patch_size[1]
            max_y = image_height - patch_size[0]    
            


            # create patch
            for _ in range(rounds):
                if count >= NUM_PATCH_REQUIRED:
                    # print(f'break')
                    break
                x = np.random.randint(0, max_x + 1)
                y = np.random.randint(0, max_y + 1)
                
                test_patch = test_img[:, y:y+patch_size[0], x:x+patch_size[1]]
                ref_patch = ref_img[:, y:y+patch_size[0], x:x+patch_size[1]]
                test_patch = torch.clamp(test_patch, min=0, max=1)

                # show_patch(test_patch.permute(1,2,0))
                # show_patch(ref_patch.permute(1,2,0))

                concatenated_patches = torch.cat((test_patch, ref_patch), dim=2)  # dim=2 for width
                to_pil = transforms.ToPILImage()
                concatenated_patches = to_pil(concatenated_patches)

                # show_patch(concatenated_patches)
                hex_unique_id = secrets.token_hex(4)
                if VELOCITY:
                    path = os.path.join(f'{output_png_dir}', f'{hex_unique_id}_{fps}_{resolution}_{bitrate}_{velocity}.png')
                    # print(f'path {path}')
                else:
                    path = os.path.join(f'{output_png_dir}', f'{hex_unique_id}_{fps}_{resolution}_{bitrate}.png')
                # print(f'path {path}')
                concatenated_patches.save(path, "png")
                count = count + 1

                # break
    return count


# extract 64x64 patch from test AND reference frames and concat to a single image
# can add velocity
if __name__ == "__main__":
    # base_directory = 'C:/Users/15142/Desktop/VRR/VRR_Frames/bistro-fast'
    base_directory = 'D:/VRR-frame/suntemple-fast'
    output_directory = 'C:/Users/15142/Desktop/VRR/VRR_Patches/suntemple-fast'
    MOTION_Dir = 'C:/Users/15142/Desktop/VRR/VRR_Motion/suntemple-fast'
    resolution_arr = [360, 480, 720, 864, 1080]
    # resolution_arr = [360]
    bitrates = [3500, 5000, 7500]
    # bitrates = [2000, 3000, 4500, 6000]
    # bitrates = [3000]

    fps_arr = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120,]
    # fps_arr = [30]
    # resolution = 360

    # Get the current date
    current_date = datetime.date.today()
    # print(current_date)
    output_dir = f'{output_directory}/{current_date}/dec_ref'

    total = 0
    NUM_PATCH_REQUIRED = 665 # 665
    VELOCITY=True

    for bitrate in bitrates:
        print(f'====================== bitrate {bitrate} ======================')
        for fps in fps_arr:
            rounds = int(132/fps) # make sure different fps has same number of patches
            count = 0 # count total number of patches generated for the fps
            for resolution in resolution_arr:
                    count = extract_and_concatenate(base_directory, bitrate, fps, resolution, \
                                                    count, rounds=rounds, output_dir=output_dir, motion_dir=MOTION_Dir, VELOCITY=VELOCITY)
                    total += count
            # for resolution in [360, 480, 720, 864, 1080]:
            while True:
                if count >= NUM_PATCH_REQUIRED:
                        break
                for resolution in resolution_arr:
                    count = extract_and_concatenate(base_directory, bitrate, fps, resolution, \
                                                    count, output_dir=output_dir, motion_dir=MOTION_Dir, VELOCITY=VELOCITY)
                    total += count
            print(f'{count} data generated for fps {fps}')
    print(f'{total} data generated.')


