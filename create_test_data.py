import shutil
import os
import imageio
import numpy as np
from utils import *
from PIL import Image
import matplotlib.pyplot as plt
from utils import *

import os
import shutil
import random  



# create test data from training data whose subfolders are label
if __name__ == "__main__":
    BASE = r'C:\Users\15142\Projects\VRR\Data\VRR_Patches\reference'
    train_folder = f'{BASE}/train'
    target_directory = f'{BASE}/validation'
    os.makedirs(target_directory, exist_ok=True)
    MOVE = True # False
    percent = 0.1


    original_folder = train_folder
    print(f'=========== original_folder {original_folder} ===========')
    for item in os.listdir(original_folder): # item is label
        label_folder = os.path.join(original_folder, item)
        all_images = os.listdir(label_folder)
        data_num = len(all_images)
        print(f'\ndata_num {data_num} in {item}')

        num_test_data = int(data_num * percent)
        print(f'all images {len(all_images)}, num_test_data {num_test_data}')
        # selected_images = random.sample(all_images, min(num_test_data, len(all_images)))
        selected_images = random.sample(all_images, num_test_data)

        new_folder_path = os.path.join(target_directory, item)
        print(f'new_folder_path {new_folder_path}')
        os.makedirs(new_folder_path, exist_ok=True)

        for image in selected_images:
            original_image_path = os.path.join(label_folder, image)
            new_image_path = os.path.join(new_folder_path, image)
            if MOVE:
                shutil.move(original_image_path, new_image_path)
                # shutil.copy(original_image_path, new_image_path)
        #     break
        # break
        
        # print(f'all images {len(os.listdir(original_folder))}')