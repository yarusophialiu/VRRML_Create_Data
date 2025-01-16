import os
import imageio
from utils import *
from PIL import Image
import matplotlib.pyplot as plt
from utils import *

import os
    
    # path = os.path.join(f'{des_path}', f'{filename}_{specs}.png')
    # print(f'path {path}')
    #     # print(f'patch \n {patch}')
    # imageio.imwrite(path, patch)
    # if SHOW:
    #     show_patch(patch)
    # return patch


def create_patch_dec(input, output, fps, patch_size=None):
     for item in os.listdir(input):
        item_path = os.path.join(input, item) # folder
        print(f'\n\n\nitempath {item_path}')

        des_item_path = os.path.join(output, f'fps{fps}', item)
        exist = os.path.exists(des_item_path)
        print(f'output {output} ')
        print(f'des_item_path {exist} {des_item_path} ')

        if not os.path.exists(des_item_path):
            os.makedirs(des_item_path, exist_ok=True)
        
        if os.path.isdir(item_path):
            for bmp in os.listdir(item_path):
                bmp_path = os.path.join(item_path, bmp)
                # print(f'bmp_path {bmp_path}')
                patch = random_patch(bmp_path, item, patch_size, des_item_path)

                # filename_with_extension = bmp_path.replace("\\", "/").split("/")[-1]
                # filename = filename_with_extension.split(".")[0]
                # path = os.path.join(f'{des_item_path}', f'{filename}_{item}.png')
                # # print(f'path {path}')
                # imageio.imwrite(path, patch)
                if SHOW:
                    show_patch(patch)

def create_patch_ref(input, output, bitrate, patch_size=None):
    print(f'input {input}')
    des_item_path = os.path.join(output, f'ref160_1080_{bitrate}_png')
    # print(f'des_item_path {des_item_path}\n')

    if not os.path.exists(des_item_path):
        os.makedirs(des_item_path, exist_ok=True)
        
    if os.path.isdir(input):
        for bmp in os.listdir(input):
            bmp_path = os.path.join(input, bmp)
            patch = random_patch2(bmp_path)
            filename = os.path.basename(bmp_path)  # This extracts the filename "10.bmp"
            number = filename.split('.')[0] 
            path = os.path.join(f'{des_item_path}', f'{number}.png')
            # print(f'path {path}')
            # imageio.imwrite(path, patch)
            if SHOW:
                show_patch(patch)
    


# create 64x64 patches from output folders in EncodeDecode
if __name__ == "__main__":
    # EncodeDecode_Dir = 'C:/Users/15142/source/repos/Falcor/Falcor/build/Source/PerceptualRendering/EncodeDecode/4000bps'
    # EncodeDecode_Dir = 'C:/Users/15142/Desktop/VRR/VRR_Patches/room_0408/8000bps'
    Frame_Dir = 'C:/Users/15142/Desktop/VRR/VRR_Frames/bistro-fast'
    # Patch_Dir = 'C:/Users/15142/Desktop/VRR_Patches/sunroom_0401/test_dataloader'
    Train_Dir = 'C:/Users/15142/Desktop/VRR/VRR_Patches/bistro-fast/'
    REFERENCE = False # True False
    # num_test_data = 20

    # TODO: change source folder
    # framerates = [60, 70, 80, 90, 100, 110, 120,]
    framerates = [60,]
    # bitrates = [4, 8, 16]
    bitrates = [2000]
    # Source_Dir = f'{EncodeDecode_Dir}/fps90'
    
    
    # patch_size = (360, 360)
    SHOW = True
    if REFERENCE:
        for bitrate in bitrates:
            Output_Dir = f'{Train_Dir}/{bitrate}bps'

            create_patch_ref(f'{Frame_Dir}/ref160_1080', Output_Dir, bitrate)
    else:
        for bitrate in bitrates:
            Output_Dir = f'{Train_Dir}/{bitrate}bps'
            os.makedirs(f'{Output_Dir}',  exist_ok=True)
            print(f'============= bitrate {bitrate} =============')
            for fps in framerates:
                Source_Dir = f'{EncodeDecode_Dir}/{bitrate}mbps/fps{fps}'
                create_patch_dec(Source_Dir, Output_Dir, fps, patch_size=(64, 64))
