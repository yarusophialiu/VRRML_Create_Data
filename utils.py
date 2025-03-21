import os
import math
import glob
import random
import imageio
import shutil
import secrets
import subprocess
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import torchvision.transforms as transforms
import subprocess
import pandas as pd
from collections import Counter


# # windows titanium
# VRRML = r'D:\VRR_data\VRRML'
# VRRML_DATA = r'D:\VRR_data\VRRML\ML'
# VRR_reference = r'D:\VRR_data\VRRMP4\reference'
# VRRMP4_reference = r'D:\VRR_data\VRRMP4\reference'
# VRR_Patches = r'D:\VRR_data\VRR_Patches'
# VRR_Motion = r'D:\VRR\VRR_Motion'


# local pc
CVVDPDIR = 'C:/Users/15142/Projects/ColorVideoVDP'
VRRMP4 = r'C:\Users\15142\Projects\VRR\VRRMP4'
VRRMP4_CVVDP = r'C:\Users\15142\Projects\VRR\VRRMP4_CVVDP'
VRRDATA = r'C:\Users\15142\Projects\VRR\Data'
VRR_Patches = f'{VRRDATA}/VRR_Patches'
VRR_Motion = r'C:\Users\15142\Projects\VRR\VRR_Motion'
VRRML = r'C:\Users\15142\Projects\VRR\Data\VRRML'
VRRML_DATA = r'C:\Users\15142\Projects\VRR\Data\VRRML\ML'
VRRMP4_reference = r'C:\Users\15142\Projects\VRR\VRRMP4\uploaded\reference'
CVVDP_EXCEL = r'C:\Users\15142\Projects\VRR\Data\VRR_Plot_HPC\data-500_1500_2000kbps' 

# # HPC
# # CVVDPDIR = 'C:/Users/15142/Projects/ColorVideoVDP'
# VRR = '/home/yl962/rds/hpc-work/VRR'
# VRRMP4_CVVDP = f'{VRR}/VRRMP4_CVVDP'
# VRRDATA = f'{VRR}/Data'
# VRR_Patches = f'{VRRDATA}/VRR_Patches'
# VRR_Motion = f'{VRR}/VRR_Motion'
# VRRML = f'{VRR_Patches}/ML'



scene_arr = ['bedroom', 'bistro', 
             'crytek_sponza', 'gallery', 
             'living_room', 'lost_empire', 
             'room', 'sibenik', 'suntemple', 
             'suntemple_statue']

# SCENES = ['bedroom', 'bistro', 'crytek_sponza', 'gallery', 'living_room', 'lost_empire', 'room', 'sibenik', 'suntemple', 'suntemple_statue']


def count_files_in_folder(folder_path):
    return len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])


def count_data_labels(training_folder, output_csv_path):
    subfolder_counts = Counter()

    # Loop through each subfolder in the training folder
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
    print(f'num_data_each_label {num_data_each_label}')

    df_subfolder_counts.to_csv(output_csv_path, index=False)



def create_train_validation_data(train_root):
    # Ensure the validation directory exists
    val_root = f"{VRRML_DATA}/validation-temp"   # Validation data root

    os.makedirs(val_root, exist_ok=True)
    total_files = 0
    total_validation_files = 0
    # Iterate over each subfolder (e.g., "360x30", "480x60", etc.)
    for subfolder in os.listdir(train_root):
        subfolder_path = os.path.join(train_root, subfolder)
        val_subfolder_path = os.path.join(val_root, subfolder)
        # print(f'subfolder {subfolder}')
        
        if os.path.isdir(subfolder_path):  # Ensure it's a directory
            os.makedirs(val_subfolder_path, exist_ok=True)  # Create validation subfolder
            
            # Get all files in the subfolder
            files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
            
            # Select 10% of files randomly
            num_val_samples = max(1, int(len(files) * 0.10))  # Ensure at least 1 file is selected
            total_validation_files += num_val_samples
            total_files += len(files)
            val_files = random.sample(files, num_val_samples)
            
            # Move selected files to the validation folder
            for file in val_files:
                # print(f'file {file}')
                shutil.move(os.path.join(subfolder_path, file), os.path.join(val_subfolder_path, file))

    train_dir = os.path.join(train_root, "train")
    os.makedirs(train_dir, exist_ok=True)
    for folder in os.listdir(train_root):
        folder_path = os.path.join(train_root, folder)
        
        # Check if it's a directory and not the "train" folder
        if os.path.isdir(folder_path) and folder != "train":
            # Move the directory into "train"
            shutil.move(folder_path, os.path.join(train_dir, folder))
    shutil.move(val_root, train_root)
    os.rename(f'{train_root}/validation-temp', f'{train_root}/validation')
    print(f'Total data {total_files}, training data {total_files - total_validation_files}, validation data {total_validation_files}')
    print(f"Saved successfully to {train_root}")

def config_create_test_data(folder):
    scenes = ['sibenik','suntemple_statue']
    return scenes, False, True, f'{folder}_test'


def frame_limit_per_fps():
    fps_arr = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120,]
    numOfFrames = 50
    for frameRate in fps_arr: 
        frameLimit = frameRate + int(numOfFrames * frameRate / 30.0) - frameRate
        print(f'frameRate {frameRate}, frameLimit {frameLimit}')


def frame_per_fps_video(fps):
    numOfFrames = 50
    frameLimit = fps + int(numOfFrames * fps / 30.0) - fps
    return frameLimit

        
def mapIdToPath(id):
    """
    we run 15 jobs/tasks (allocate 13 gpus) at one time, each scene has 45 clips, so we run 3 times
    for each task id, we run videos for 1 scene, 1 seg, 1 speed, i.e. for loop 50 * 13 = 650 videos
    e.g. sbatch --array=0-14:1 -A STARS-SL3-GPU submission_script

    id is from 0-44, map id -> path, seg, speed

    e.g. id 0 -> paths[0], segs[0], speeds[0]
         id 1 -> paths[0], segs[0], speeds[1]
    """
    pathIdx = int(math.floor(id/9))
    segIdx = int(math.floor((id - pathIdx * 9) / 3))
    speedIdx = (id - pathIdx * 9) % 3
    paths = [1, 2, 3, 4, 5]
    segs = [1, 2, 3,]
    speeds = [1, 2, 3,]
#    print(f'pathIdx {pathIdx}, segIdx {segIdx} speedIdx {speedIdx}')
    return paths[pathIdx], segs[segIdx], speeds[speedIdx]



def mapPathToId(path, seg, speed):
    id = (path-1) * 9 + (seg-1) * 3 + speed - 1
    print(f'id {id}')
    return id


def save_or_show_image(input_image, path, format="png", SAVE=True, SHOW=False):
    """
    image is torch tensor
    """
    # Convert to PIL image for visualization
    to_pil = transforms.ToPILImage()
    image = to_pil(input_image)
    if SAVE:
        image.save(path, format)
    if SHOW:
        plt.imshow(image)
        plt.axis("off")
        plt.show()



def conda_init():
        print(f'Init conda')
        activate_command = f'conda init && conda activate cvvdp'

        try:
            subprocess.run(activate_command, check=True, shell=True)
            # print("Command executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running the command: {e}")


def extract_metadata(filename):
        dec_name = os.path.basename(filename)

        parts = dec_name.split('_')     
        fps = float(parts[3])
        resolution = int(parts[4])  # Assuming you might need this for something else
        bitrate = int(parts[5].split('.')[0])  # Remove .png and convert to integer
        
        # print(f'\nnewRefPath {newRefPath}')
        # print(f'newDecPath fps, resolution, bitrate \n{dec_name} {fps} {resolution} {bitrate}\n')
        print(f'{dec_name} {fps} {resolution} {bitrate}')

# make sure on temp-resample branch
def runCVVDP_image(newRefPath, newDecPath):
        extract_metadata(newDecPath)

        # command = f"cvvdp --test {newDecPath} --ref {newRefPath} --display standard_fhd --full-screen-resize bilinear --temp-resample"
        command = f"cvvdp --test {newDecPath} --ref {newRefPath} --display standard_fhd"
        # command = cvvdp --test C:/RFL/VRR/VRRMP4/4000Mbps/fps60/dec60_360/dec* --ref C:/RFL/VRR/VRRMP4/ref160_1080/ref* --display standard_fhd --full-screen-resize bilinear --temp-resample
        # command = cvvdp --test 4.bmp --ref 2.bmp --display standard_fhd --full-screen-resize bilinear --temp-resample

        # activate_command = f'conda init && conda activate cvvdp && cd "{CVVDPDIR}" && git checkout temp-resample'
        activate_command = f'cd "{CVVDPDIR}" && {command}'
        # activate_command = f'conda init && conda activate cvvdp && cd "{CVVDPDIR}" && git checkout temp-resample && {command}'

        try:
            subprocess.run(activate_command, check=True, shell=True)
            # print("Command executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running the command: {e}")



# Floor function that should be robust to the floating point precision issues
def safe_floor(x):
    x_f = math.floor(x)
    return x_f if (x-x_f)<(1-1e-6) else x_f+1



def random_patch2(bmp_path, patch_size=None, SHOW=False):
# def random_patch(bmp_path, specs, des_path, patch_size=None, SHOW=False):
    """
    bmp_path: C:/Users/15142/Desktop/test\30_720_1000\10.bmp
    specs: e.g. 30_720_1000
    """
    # print(f'\ndes_path {des_path}')
    # print(f'bmp_path {bmp_path}')

    bmp_image = Image.open(bmp_path) 
    image = np.array(bmp_image)
    image_width, image_height = image.shape[1], image.shape[0]
    # print(f'image_width, image_height {image_width, image_height}')

    if patch_size == None:
        # print('no patch size')
        patch_size = (image_width, image_height)
        patch = image
    else:
        max_x = image_width - patch_size[1]
        max_y = image_height - patch_size[0]
        
        # Randomly select the x and y coordinates for the top-left corner of the patch
        x = np.random.randint(0, max_x + 1)
        y = np.random.randint(0, max_y + 1)
        
        # Extract the patch from the image array
        patch = image[y:y+patch_size[0], x:x+patch_size[1]]
    
    return patch



def show_patch(patch):
    plt.imshow(patch)
    plt.axis('off')  # Hide axis
    plt.show()



def get_frame_value(filename, frame_num):
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.strip().startswith(str(frame_num) + " "):
                    # Extract the value after the framenum and whitespace
                    value = line.strip().split()[1]
                    return value
        return "Frame number not found."
    except FileNotFoundError:
        return "File not found."
    

def count_files(directory):
    """Count the number of files in a directory."""
    # Use os.listdir to get all entries in the directory
    # Use os.path.isfile to filter these entries to only files
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return len(files)



def random_patch(bmp_path, specs, patch_size, output_dir, count=0, rounds=0, V=None, SHOW=False, NUM_PATCH_REQUIRED=0):
    """
    bmp_path: C:/Users/15142/Desktop/test\30_720_1000\10.bmp
    specs: e.g. 30_720_1000
    """
    filename_with_extension = bmp_path.replace("\\", "/").split("/")[-1]
    filename = filename_with_extension.split(".")[0] # frame number
    # print(f'\nrandom patch rounds {rounds}, count {count}')

    bmp_image = Image.open(bmp_path) 
    image = np.array(bmp_image)
    image_width, image_height = image.shape[1], image.shape[0]
    max_x = image_width - patch_size[1]
    max_y = image_height - patch_size[0]

    patch = None
    for _ in range(rounds):
        if count >= NUM_PATCH_REQUIRED:
            # print(f'break')
            break
        # print(f'\n\n\ni {i}')
        # Randomly select the x and y coordinates for the top-left corner of the patch
        x = np.random.randint(0, max_x + 1)
        y = np.random.randint(0, max_y + 1)
        
        # Extract the patch from the image array
        patch = image[y:y+patch_size[0], x:x+patch_size[1]]

        hex_unique_id = secrets.token_hex(4)
        if V:
            # print(f'velocity {V}')
            path = os.path.join(f'{output_dir}', f'{hex_unique_id}_{filename}_{specs}_{V}.png')
            # print(f'path {path}')
        else:
            path = os.path.join(f'{output_dir}', f'{hex_unique_id}_{filename}_{specs}.png')
        # print(f'path {path}')
        # print(f'patch \n {patch}')
        count += 1
        imageio.imwrite(path, patch)
    if SHOW:
        show_patch(patch)
    return patch, count




def delete_files(directory_path, files_to_delete):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # List all files in the directory
        # files = os.listdir(directory_path)

        for file_to_delete in files_to_delete:
            file_path = os.path.join(directory_path, file_to_delete)

            # Check if the file exists before attempting to delete
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
    else:
        print(f"Directory not found: {directory_path}")

def delete_files_range(directory_path, num_to_delete):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        for i in range(num_to_delete):
            # file_path = os.path.join(directory_path, file_to_delete)
            file_path = str(i) + '.bmp'
            file_to_delete = os.path.join(directory_path, file_path)

            print(f'file path {file_to_delete}')

            # Check if the file exists before attempting to delete
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
                print(f"Deleted: {file_to_delete}")
            else:
                print(f"File not found: {file_to_delete}")

        rename_files(directory_path)
    else:
        print(f"Directory not found: {directory_path}")


def bmp_to_png(bmp_path):
    with Image.open(bmp_path) as img:
        # Convert the image to RGB mode if it's not already in RGB mode
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    
    
def rename_files(directory_path):
     # rename files to 1.bmp, 2.bmp...
    file_names = os.listdir(directory_path)
    file_names.sort()  # Sort the file names

    for i, file_name in enumerate(file_names, start=1):
        old_path = os.path.join(directory_path, file_name)
        new_path = os.path.join(directory_path, f"{i}.bmp")
        os.rename(old_path, new_path)
        print(f"Renamed: {old_path} -> {new_path}")


def emptyFolder(folder_path, deleteBMP=False):
    if deleteBMP:
        # Use glob to get a list of all files in the folder
        files_to_delete = glob.glob(os.path.join(folder_path, '*'))

        # Delete each file in the list
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                # print(f"File '{file_path}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting file '{file_path}': {e}")




def compute_motion(motion_file):
    with open(motion_file, 'r') as file:
        lines = file.readlines()

    # Parse the velocity values from the lines
    velocities = [float(line.split()[1]) for line in lines]
    # print(f'velocities {velocities[2:]}')

    # Calculate the average velocity from count 2 to the end
    average_velocity = sum(velocities[2:]) / len(velocities[2:])
    average_velocity = round(average_velocity, 3)

    # print("Average velocity from count 2 to the end:", round(average_velocity, 3))
    return average_velocity


refresh_rate = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
bistro_max_comb_per_sequence = {'path1_seg1_1': [[30, 1080], [40, 1080], [50, 1080], [50, 1080]], 'path1_seg1_2': [[70, 720], [80, 720], [80, 1080], [80, 1080]], 'path1_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[50, 720], [70, 1080], [80, 1080], [80, 1080]], 'path1_seg2_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[50, 720], [50, 1080], [50, 1080], [60, 1080]], 'path1_seg3_2': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path1_seg3_3': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[60, 720], [80, 720], [80, 720], [80, 1080]], 'path2_seg1_2': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path2_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[60, 720], [80, 720], [80, 1080], [80, 1080]], 'path2_seg2_2': [[90, 480], [110, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[120, 360], [120, 480], [120, 480], [120, 720]], 'path2_seg3_1': [[40, 720], [50, 1080], [60, 1080], [60, 1080]], 'path2_seg3_2': [[80, 720], [90, 720], [110, 720], [120, 720]], 'path2_seg3_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[90, 720], [100, 720], [110, 720], [120, 720]], 'path3_seg1_2': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg2_1': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path3_seg2_2': [[80, 720], [100, 720], [110, 720], [120, 720]], 'path3_seg2_3': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[80, 720], [90, 720], [110, 720], [120, 1080]], 'path3_seg3_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg3_3': [[120, 480], [120, 480], [120, 480], [120, 720]], 'path4_seg1_1': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path4_seg1_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path4_seg2_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_3': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg3_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg3_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path5_seg1_1': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path5_seg1_2': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path5_seg1_3': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[80, 720], [90, 720], [120, 720], [120, 720]], 'path5_seg2_2': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg3_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]]}
room_max_comb_per_sequence = {'path1_seg1_1': [[60, 720], [70, 720], [90, 720], [110, 720]], 'path1_seg1_2': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path1_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path1_seg2_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[120, 360], [120, 360], [120, 360], [120, 360]], 'path1_seg3_2': [[120, 480], [120, 360], [120, 360], [120, 360]], 'path1_seg3_3': [[120, 360], [120, 480], [120, 360], [120, 360]], 'path2_seg1_1': [[60, 720], [110, 720], [110, 720], [110, 720]], 'path2_seg1_2': [[80, 720], [110, 720], [110, 720], [120, 720]], 'path2_seg1_3': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path2_seg2_2': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[110, 720], [110, 720], [110, 720], [110, 720]], 'path2_seg3_1': [[60, 720], [70, 720], [80, 720], [90, 720]], 'path2_seg3_2': [[70, 720], [80, 720], [80, 720], [110, 720]], 'path2_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[60, 720], [100, 720], [100, 720], [110, 720]], 'path3_seg1_2': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path3_seg1_3': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg2_1': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path3_seg2_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg2_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg3_2': [[80, 720], [90, 720], [120, 720], [120, 720]], 'path3_seg3_3': [[100, 720], [100, 720], [100, 720], [100, 720]], 'path4_seg1_1': [[110, 720], [110, 720], [110, 720], [120, 720]], 'path4_seg1_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[80, 720], [90, 720], [120, 720], [120, 720]], 'path4_seg3_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg1_1': [[70, 720], [80, 720], [110, 720], [110, 720]], 'path5_seg1_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[120, 480], [120, 480], [120, 480], [120, 480]], 'path5_seg2_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg2_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[80, 720], [110, 720], [110, 720], [90, 1080]], 'path5_seg3_2': [[100, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[120, 720], [120, 720], [120, 720], [120, 720]]}
bedroom_max_comb_per_sequence = {'path1_seg1_1': [[30, 720], [40, 720], [50, 720], [40, 1080]], 'path1_seg1_2': [[50, 720], [60, 720], [70, 720], [70, 720]], 'path1_seg1_3': [[60, 720], [80, 720], [80, 720], [80, 720]], 'path1_seg2_1': [[40, 720], [50, 720], [60, 720], [80, 720]], 'path1_seg2_2': [[60, 720], [60, 720], [80, 720], [100, 720]], 'path1_seg2_3': [[70, 720], [80, 720], [110, 720], [110, 720]], 'path1_seg3_1': [[50, 720], [60, 720], [110, 720], [110, 720]], 'path1_seg3_2': [[60, 720], [70, 720], [110, 720], [110, 720]], 'path1_seg3_3': [[80, 720], [80, 720], [90, 720], [90, 720]], 'path2_seg1_1': [[40, 720], [60, 720], [90, 720], [110, 720]], 'path2_seg1_2': [[50, 720], [60, 720], [80, 720], [110, 720]], 'path2_seg1_3': [[60, 720], [80, 720], [90, 720], [90, 720]], 'path2_seg2_1': [[50, 720], [60, 720], [80, 720], [80, 720]], 'path2_seg2_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[100, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_1': [[40, 720], [60, 720], [80, 720], [80, 720]], 'path2_seg3_2': [[60, 720], [80, 720], [110, 720], [120, 720]], 'path2_seg3_3': [[60, 480], [80, 720], [90, 720], [110, 720]], 'path3_seg1_1': [[40, 720], [50, 720], [70, 720], [80, 720]], 'path3_seg1_2': [[50, 720], [80, 720], [80, 720], [90, 720]], 'path3_seg1_3': [[60, 720], [70, 720], [80, 720], [90, 720]], 'path3_seg2_1': [[30, 720], [50, 720], [60, 720], [70, 720]], 'path3_seg2_2': [[50, 720], [60, 720], [70, 720], [80, 720]], 'path3_seg2_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[60, 720], [80, 720], [90, 720], [110, 720]], 'path3_seg3_2': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg3_3': [[110, 480], [110, 720], [110, 720], [110, 720]], 'path4_seg1_1': [[60, 720], [80, 720], [80, 720], [80, 720]], 'path4_seg1_2': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path4_seg1_3': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path4_seg2_2': [[90, 720], [100, 720], [120, 720], [120, 720]], 'path4_seg2_3': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[120, 480], [120, 480], [120, 720], [120, 720]], 'path4_seg3_2': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg3_3': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg1_1': [[60, 720], [80, 720], [110, 720], [110, 720]], 'path5_seg1_2': [[90, 720], [90, 720], [110, 720], [120, 720]], 'path5_seg1_3': [[60, 720], [90, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[40, 720], [50, 720], [60, 720], [60, 720]], 'path5_seg2_2': [[70, 720], [80, 720], [110, 720], [110, 720]], 'path5_seg2_3': [[110, 480], [110, 720], [110, 720], [110, 720]], 'path5_seg3_1': [[60, 720], [80, 720], [80, 720], [110, 720]], 'path5_seg3_2': [[80, 720], [90, 720], [110, 720], [120, 720]], 'path5_seg3_3': [[110, 480], [110, 720], [110, 720], [110, 720]]}
crytek_sponza_max_comb_per_sequence = {'path1_seg1_1': [[60, 720], [70, 1080], [80, 1080], [80, 1080]], 'path1_seg1_2': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg1_3': [[100, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[50, 720], [40, 1080], [50, 1080], [60, 1080]], 'path1_seg2_2': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path1_seg2_3': [[80, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[50, 720], [40, 1080], [50, 1080], [50, 1080]], 'path1_seg3_2': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path1_seg3_3': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[30, 720], [40, 1080], [40, 1080], [50, 1080]], 'path2_seg1_2': [[80, 720], [80, 720], [90, 720], [90, 720]], 'path2_seg1_3': [[80, 480], [90, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[30, 720], [40, 1080], [40, 1080], [40, 1080]], 'path2_seg2_2': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path2_seg2_3': [[70, 720], [80, 720], [90, 720], [90, 720]], 'path2_seg3_1': [[40, 720], [50, 720], [60, 720], [50, 1080]], 'path2_seg3_2': [[80, 720], [80, 720], [90, 720], [110, 720]], 'path2_seg3_3': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[30, 720], [50, 720], [60, 720], [60, 720]], 'path3_seg1_2': [[80, 720], [80, 720], [90, 720], [110, 720]], 'path3_seg1_3': [[80, 720], [100, 720], [110, 720], [120, 720]], 'path3_seg2_1': [[40, 720], [50, 720], [60, 720], [50, 1080]], 'path3_seg2_2': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path3_seg2_3': [[80, 720], [90, 720], [90, 720], [110, 720]], 'path3_seg3_1': [[40, 720], [60, 720], [70, 720], [50, 1080]], 'path3_seg3_2': [[60, 720], [70, 720], [80, 720], [110, 720]], 'path3_seg3_3': [[70, 720], [80, 720], [90, 720], [110, 720]], 'path4_seg1_1': [[30, 720], [30, 1080], [30, 1080], [30, 1080]], 'path4_seg1_2': [[40, 720], [50, 720], [40, 1080], [50, 1080]], 'path4_seg1_3': [[50, 720], [50, 720], [60, 720], [60, 720]], 'path4_seg2_1': [[30, 720], [40, 720], [30, 1080], [30, 1080]], 'path4_seg2_2': [[30, 720], [50, 720], [50, 720], [40, 1080]], 'path4_seg2_3': [[40, 720], [50, 720], [60, 720], [70, 720]], 'path4_seg3_1': [[30, 720], [30, 1080], [30, 1080], [30, 1080]], 'path4_seg3_2': [[40, 720], [50, 720], [40, 1080], [50, 1080]], 'path4_seg3_3': [[40, 720], [60, 720], [50, 1080], [60, 1080]], 'path5_seg1_1': [[30, 720], [40, 1080], [40, 1080], [50, 1080]], 'path5_seg1_2': [[60, 720], [80, 720], [90, 720], [100, 720]], 'path5_seg1_3': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path5_seg2_1': [[50, 720], [60, 720], [70, 720], [60, 1080]], 'path5_seg2_2': [[80, 480], [90, 720], [110, 720], [110, 720]], 'path5_seg2_3': [[80, 480], [90, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[60, 720], [80, 720], [90, 720], [90, 720]], 'path5_seg3_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[110, 480], [110, 480], [120, 720], [120, 720]]}
gallery_max_comb_per_sequence = {'path1_seg1_1': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg1_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[80, 720], [100, 720], [110, 720], [120, 1080]], 'path1_seg2_2': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[100, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[80, 720], [80, 720], [90, 1080], [90, 1080]], 'path1_seg3_2': [[90, 720], [90, 720], [110, 720], [120, 864]], 'path1_seg3_3': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[50, 720], [50, 864], [60, 1080], [70, 1080]], 'path2_seg1_2': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg1_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[60, 720], [60, 720], [70, 864], [80, 1080]], 'path2_seg2_2': [[80, 480], [90, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_1': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg3_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_3': [[120, 360], [120, 480], [120, 720], [120, 720]], 'path3_seg1_1': [[80, 480], [90, 720], [110, 720], [120, 720]], 'path3_seg1_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg2_1': [[50, 720], [80, 720], [80, 1080], [80, 1080]], 'path3_seg2_2': [[70, 720], [80, 720], [110, 720], [120, 864]], 'path3_seg2_3': [[70, 720], [90, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[50, 720], [60, 1080], [60, 1080], [70, 1080]], 'path3_seg3_2': [[80, 720], [80, 720], [110, 720], [110, 1080]], 'path3_seg3_3': [[80, 720], [80, 720], [120, 720], [120, 720]], 'path4_seg1_1': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path4_seg1_2': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path4_seg1_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_2': [[120, 480], [120, 480], [120, 480], [120, 720]], 'path4_seg2_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path4_seg3_1': [[50, 720], [70, 720], [80, 720], [80, 720]], 'path4_seg3_2': [[110, 480], [120, 480], [120, 720], [120, 720]], 'path4_seg3_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path5_seg1_1': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg1_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[60, 720], [80, 720], [80, 720], [110, 720]], 'path5_seg2_2': [[80, 720], [90, 720], [120, 720], [110, 1080]], 'path5_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path5_seg3_2': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]]}
living_room_max_comb_per_sequence = {'path1_seg1_1': [[90, 720], [110, 720], [120, 864], [120, 864]], 'path1_seg1_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg1_3': [[120, 480], [120, 480], [120, 720], [120, 720]], 'path1_seg2_1': [[110, 720], [110, 720], [110, 720], [110, 720]], 'path1_seg2_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[90, 720], [110, 720], [110, 1080], [120, 1080]], 'path1_seg3_2': [[100, 720], [120, 720], [120, 864], [120, 864]], 'path1_seg3_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path2_seg1_2': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path2_seg1_3': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path2_seg2_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_1': [[80, 720], [110, 720], [120, 1080], [120, 1080]], 'path2_seg3_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[110, 720], [110, 720], [110, 720], [110, 720]], 'path3_seg1_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg2_1': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path3_seg2_2': [[120, 360], [120, 480], [120, 480], [120, 720]], 'path3_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path3_seg3_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg1_1': [[110, 720], [110, 720], [110, 720], [110, 720]], 'path4_seg1_2': [[110, 720], [110, 720], [110, 720], [120, 720]], 'path4_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[60, 720], [60, 1080], [80, 1080], [80, 1080]], 'path4_seg2_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[80, 720], [100, 720], [120, 1080], [120, 1080]], 'path4_seg3_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg1_1': [[70, 720], [80, 720], [110, 720], [110, 720]], 'path5_seg1_2': [[120, 480], [120, 480], [120, 480], [120, 480]], 'path5_seg1_3': [[120, 480], [120, 480], [120, 480], [120, 480]], 'path5_seg2_1': [[80, 720], [110, 720], [110, 720], [110, 1080]], 'path5_seg2_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg2_3': [[120, 360], [120, 480], [120, 720], [120, 720]], 'path5_seg3_1': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path5_seg3_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[120, 720], [120, 720], [120, 720], [120, 720]]}
lost_empire_max_comb_per_sequence = {'path1_seg1_1': [[50, 720], [60, 720], [60, 720], [60, 1080]], 'path1_seg1_2': [[70, 720], [80, 720], [80, 720], [90, 720]], 'path1_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_2': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg3_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[70, 720], [90, 720], [110, 720], [110, 720]], 'path2_seg1_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[70, 720], [90, 720], [110, 720], [110, 720]], 'path2_seg2_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_1': [[70, 720], [90, 720], [110, 720], [110, 720]], 'path2_seg3_2': [[100, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[90, 720], [100, 720], [110, 720], [120, 720]], 'path3_seg1_2': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg1_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg2_1': [[50, 720], [80, 720], [90, 720], [120, 720]], 'path3_seg2_2': [[80, 720], [90, 720], [110, 720], [110, 864]], 'path3_seg2_3': [[110, 480], [110, 720], [110, 720], [110, 720]], 'path3_seg3_1': [[40, 720], [50, 1080], [60, 1080], [60, 1080]], 'path3_seg3_2': [[40, 720], [50, 1080], [60, 1080], [60, 1080]], 'path3_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg1_1': [[50, 720], [60, 720], [80, 720], [80, 720]], 'path4_seg1_2': [[80, 720], [90, 720], [110, 720], [110, 720]], 'path4_seg1_3': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[50, 720], [80, 720], [80, 720], [80, 1080]], 'path4_seg2_2': [[70, 720], [90, 720], [110, 720], [120, 720]], 'path4_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[60, 720], [70, 720], [80, 720], [80, 1080]], 'path4_seg3_2': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path4_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg1_1': [[80, 480], [80, 720], [100, 720], [120, 720]], 'path5_seg1_2': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg1_3': [[120, 480], [120, 480], [120, 720], [120, 720]], 'path5_seg2_1': [[70, 720], [80, 720], [80, 720], [90, 720]], 'path5_seg2_2': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg2_3': [[120, 360], [120, 480], [120, 720], [120, 720]], 'path5_seg3_1': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_2': [[120, 480], [120, 480], [120, 480], [120, 480]], 'path5_seg3_3': [[120, 360], [120, 480], [120, 480], [120, 480]]}
sibenik_max_comb_per_sequence = {'path1_seg1_1': [[80, 720], [90, 720], [120, 720], [120, 720]], 'path1_seg1_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg1_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[80, 720], [110, 720], [110, 720], [120, 720]], 'path1_seg2_2': [[100, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[50, 720], [70, 1080], [80, 1080], [80, 1080]], 'path1_seg3_2': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path1_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[50, 720], [50, 1080], [60, 1080], [70, 1080]], 'path2_seg1_2': [[80, 720], [90, 720], [110, 720], [120, 720]], 'path2_seg1_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[50, 720], [60, 720], [70, 864], [80, 1080]], 'path2_seg2_2': [[90, 720], [110, 720], [110, 720], [120, 720]], 'path2_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_1': [[60, 720], [80, 720], [110, 720], [110, 720]], 'path2_seg3_2': [[90, 480], [110, 720], [120, 720], [120, 720]], 'path2_seg3_3': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[50, 720], [60, 864], [80, 1080], [80, 1080]], 'path3_seg1_2': [[80, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg1_3': [[110, 480], [110, 720], [120, 720], [120, 720]], 'path3_seg2_1': [[60, 720], [80, 720], [80, 1080], [90, 1080]], 'path3_seg2_2': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg2_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[80, 720], [80, 720], [110, 720], [120, 1080]], 'path3_seg3_2': [[110, 480], [120, 480], [120, 720], [120, 720]], 'path3_seg3_3': [[120, 360], [120, 480], [120, 720], [120, 720]], 'path4_seg1_1': [[90, 720], [110, 720], [120, 720], [120, 720]], 'path4_seg1_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[120, 480], [120, 480], [120, 480], [120, 480]], 'path4_seg2_2': [[120, 480], [120, 480], [120, 720], [120, 720]], 'path4_seg2_3': [[120, 480], [120, 480], [120, 720], [120, 720]], 'path4_seg3_1': [[70, 720], [90, 720], [100, 720], [120, 720]], 'path4_seg3_2': [[120, 360], [120, 480], [120, 720], [120, 720]], 'path4_seg3_3': [[120, 480], [120, 480], [120, 480], [120, 480]], 'path5_seg1_1': [[80, 720], [80, 720], [100, 720], [100, 1080]], 'path5_seg1_2': [[110, 720], [110, 720], [120, 720], [120, 1080]], 'path5_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[50, 720], [60, 720], [80, 720], [80, 1080]], 'path5_seg2_2': [[80, 720], [90, 720], [110, 720], [120, 720]], 'path5_seg2_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path5_seg3_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[120, 480], [120, 480], [120, 720], [120, 720]]}
suntemple_max_comb_per_sequence = {'path1_seg1_1': [[50, 720], [60, 720], [60, 1080], [60, 1080]], 'path1_seg1_2': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path1_seg1_3': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[40, 720], [60, 720], [60, 1080], [60, 1080]], 'path1_seg2_2': [[60, 720], [80, 720], [120, 720], [120, 720]], 'path1_seg2_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path1_seg3_1': [[50, 720], [60, 720], [80, 720], [80, 720]], 'path1_seg3_2': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path1_seg3_3': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[40, 720], [50, 720], [60, 720], [60, 720]], 'path2_seg1_2': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path2_seg1_3': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg2_1': [[40, 720], [60, 720], [70, 720], [80, 720]], 'path2_seg2_2': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_1': [[60, 720], [70, 720], [80, 720], [110, 720]], 'path2_seg3_2': [[80, 720], [110, 720], [120, 720], [120, 720]], 'path2_seg3_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[80, 720], [90, 720], [120, 720], [120, 720]], 'path3_seg1_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_3': [[80, 480], [120, 480], [110, 720], [120, 720]], 'path3_seg2_1': [[70, 720], [80, 720], [80, 720], [110, 720]], 'path3_seg2_2': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg2_3': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[60, 720], [70, 720], [80, 720], [100, 720]], 'path3_seg3_2': [[60, 720], [80, 720], [110, 720], [120, 720]], 'path3_seg3_3': [[110, 720], [110, 720], [120, 720], [120, 720]], 'path4_seg1_1': [[70, 720], [90, 720], [90, 720], [110, 720]], 'path4_seg1_2': [[90, 720], [90, 720], [100, 720], [110, 720]], 'path4_seg1_3': [[90, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[50, 720], [50, 720], [60, 720], [70, 720]], 'path4_seg2_2': [[60, 720], [80, 720], [80, 720], [80, 720]], 'path4_seg2_3': [[70, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[60, 720], [80, 720], [110, 720], [80, 1080]], 'path4_seg3_2': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path4_seg3_3': [[90, 720], [110, 720], [110, 720], [120, 720]], 'path5_seg1_1': [[80, 720], [110, 720], [110, 1080], [110, 1080]], 'path5_seg1_2': [[120, 720], [120, 720], [120, 1080], [120, 1080]], 'path5_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[80, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg2_2': [[90, 480], [90, 720], [90, 720], [90, 720]], 'path5_seg2_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_2': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[110, 480], [110, 720], [110, 720], [110, 720]]}
suntemple_statue_max_comb_per_sequence = {'path1_seg1_1': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg1_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path1_seg2_1': [[80, 720], [100, 720], [110, 720], [110, 1080]], 'path1_seg2_2': [[110, 720], [110, 720], [120, 1080], [120, 1080]], 'path1_seg2_3': [[110, 720], [110, 720], [110, 1080], [110, 1080]], 'path1_seg3_1': [[50, 720], [60, 1080], [60, 1080], [80, 1080]], 'path1_seg3_2': [[80, 720], [110, 720], [110, 1080], [110, 1080]], 'path1_seg3_3': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg1_1': [[50, 720], [50, 1080], [60, 1080], [80, 1080]], 'path2_seg1_2': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg1_3': [[110, 480], [120, 480], [120, 720], [120, 720]], 'path2_seg2_1': [[50, 720], [60, 864], [80, 1080], [80, 1080]], 'path2_seg2_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg2_3': [[110, 480], [120, 720], [120, 720], [120, 720]], 'path2_seg3_1': [[80, 720], [110, 720], [110, 720], [110, 720]], 'path2_seg3_2': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path2_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path3_seg1_1': [[40, 720], [50, 1080], [50, 1080], [60, 1080]], 'path3_seg1_2': [[80, 720], [80, 720], [110, 720], [110, 720]], 'path3_seg1_3': [[90, 720], [110, 720], [110, 720], [110, 720]], 'path3_seg2_1': [[80, 720], [110, 864], [110, 864], [110, 1080]], 'path3_seg2_2': [[70, 720], [110, 864], [120, 1080], [120, 1080]], 'path3_seg2_3': [[90, 720], [90, 720], [120, 720], [120, 720]], 'path3_seg3_1': [[70, 720], [60, 1080], [80, 1080], [80, 1080]], 'path3_seg3_2': [[80, 720], [110, 720], [110, 864], [120, 864]], 'path3_seg3_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg1_1': [[90, 720], [110, 720], [110, 720], [110, 1080]], 'path4_seg1_2': [[120, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path4_seg2_1': [[110, 720], [110, 720], [110, 720], [110, 720]], 'path4_seg2_2': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg2_3': [[90, 720], [120, 720], [120, 720], [120, 720]], 'path4_seg3_1': [[40, 864], [40, 1080], [60, 1080], [80, 1080]], 'path4_seg3_2': [[60, 864], [70, 1080], [80, 1080], [80, 1080]], 'path4_seg3_3': [[100, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg1_1': [[40, 1080], [60, 1080], [60, 1080], [80, 1080]], 'path5_seg1_2': [[120, 720], [120, 720], [120, 1080], [120, 1080]], 'path5_seg1_3': [[120, 480], [120, 720], [120, 720], [120, 720]], 'path5_seg2_1': [[70, 1080], [80, 1080], [80, 1080], [80, 1080]], 'path5_seg2_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg2_3': [[120, 480], [110, 720], [120, 720], [120, 720]], 'path5_seg3_1': [[70, 720], [80, 720], [110, 720], [110, 1080]], 'path5_seg3_2': [[110, 720], [120, 720], [120, 720], [120, 720]], 'path5_seg3_3': [[120, 720], [120, 720], [120, 720], [120, 720]]}

scene_velocity_dicts = {
        'bedroom': bedroom_max_comb_per_sequence,
        'bistro': bistro_max_comb_per_sequence,
        'crytek_sponza': crytek_sponza_max_comb_per_sequence,
        'gallery': gallery_max_comb_per_sequence,
        'living_room': living_room_max_comb_per_sequence,
        'lost_empire': lost_empire_max_comb_per_sequence,
        'room': room_max_comb_per_sequence,
        'sibenik': sibenik_max_comb_per_sequence,
        'suntemple': suntemple_max_comb_per_sequence,
        'suntemple_statue': suntemple_statue_max_comb_per_sequence
    }

# drop jod 0.25
bedroom_comb_drop_JOD = {'path1_seg1_1': [[30, 720], [30, 720], [30, 720], [30, 720]], 'path1_seg1_2': [[40, 720], [40, 720], [50, 720], [50, 720]], 'path1_seg1_3': [[50, 720], [50, 720], [60, 720], [60, 720]], 'path1_seg2_1': [[30, 720], [40, 720], [40, 720], [40, 720]], 'path1_seg2_2': [[50, 480], [50, 720], [50, 720], [60, 720]], 'path1_seg2_3': [[50, 480], [70, 480], [60, 720], [70, 720]], 'path1_seg3_1': [[40, 720], [40, 720], [50, 720], [50, 720]], 'path1_seg3_2': [[50, 480], [80, 480], [60, 720], [70, 720]], 'path1_seg3_3': [[60, 480], [80, 480], [80, 480], [80, 720]], 'path2_seg1_1': [[40, 480], [40, 720], [40, 720], [40, 720]], 'path2_seg1_2': [[40, 480], [60, 480], [60, 720], [60, 720]], 'path2_seg1_3': [[50, 480], [60, 480], [70, 480], [80, 480]], 'path2_seg2_1': [[50, 480], [50, 720], [50, 720], [50, 720]], 'path2_seg2_2': [[70, 360], [100, 360], [100, 480], [110, 480]], 'path2_seg2_3': [[60, 360], [80, 360], [80, 480], [90, 480]], 'path2_seg3_1': [[30, 720], [30, 720], [30, 720], [40, 720]], 'path2_seg3_2': [[50, 360], [60, 480], [70, 480], [80, 480]], 'path2_seg3_3': [[50, 360], [60, 480], [70, 480], [80, 480]], 'path3_seg1_1': [[30, 720], [40, 720], [40, 720], [40, 720]], 'path3_seg1_2': [[50, 480], [50, 720], [60, 720], [60, 720]], 'path3_seg1_3': [[60, 360], [60, 480], [80, 480], [80, 480]], 'path3_seg2_1': [[30, 720], [30, 720], [30, 720], [30, 720]], 'path3_seg2_2': [[40, 480], [50, 480], [70, 480], [50, 720]], 'path3_seg2_3': [[70, 360], [80, 480], [90, 480], [100, 480]], 'path3_seg3_1': [[50, 480], [60, 480], [80, 480], [60, 720]], 'path3_seg3_2': [[60, 360], [90, 360], [80, 480], [80, 480]], 'path3_seg3_3': [[80, 360], [90, 360], [90, 360], [90, 360]], 'path4_seg1_1': [[50, 480], [50, 720], [60, 720], [60, 720]], 'path4_seg1_2': [[60, 360], [70, 480], [70, 720], [80, 720]], 'path4_seg1_3': [[60, 360], [70, 480], [80, 480], [100, 480]], 'path4_seg2_1': [[60, 720], [70, 720], [70, 720], [80, 720]], 'path4_seg2_2': [[70, 480], [70, 720], [80, 720], [80, 720]], 'path4_seg2_3': [[80, 360], [90, 480], [110, 480], [110, 480]], 'path4_seg3_1': [[100, 360], [110, 360], [110, 360], [110, 360]], 'path4_seg3_2': [[90, 360], [120, 480], [100, 720], [100, 720]], 'path4_seg3_3': [[80, 360], [80, 480], [90, 480], [110, 480]], 'path5_seg1_1': [[60, 480], [60, 720], [70, 720], [80, 720]], 'path5_seg1_2': [[60, 360], [70, 480], [80, 480], [90, 480]], 'path5_seg1_3': [[50, 360], [60, 480], [80, 480], [90, 480]], 'path5_seg2_1': [[30, 720], [40, 720], [40, 720], [40, 720]], 'path5_seg2_2': [[70, 360], [80, 480], [100, 480], [110, 480]], 'path5_seg2_3': [[80, 360], [90, 360], [110, 360], [110, 360]], 'path5_seg3_1': [[50, 720], [60, 720], [60, 720], [70, 720]], 'path5_seg3_2': [[70, 480], [80, 720], [80, 720], [80, 720]], 'path5_seg3_3': [[80, 360], [80, 480], [90, 480], [90, 480]]}
bistro_comb_drop_JOD = {'path1_seg1_1': [[30, 720], [30, 1080], [40, 1080], [40, 1080]], 'path1_seg1_2': [[40, 720], [60, 720], [60, 720], [70, 720]], 'path1_seg1_3': [[80, 360], [90, 480], [120, 480], [90, 720]], 'path1_seg2_1': [[40, 720], [50, 720], [70, 720], [70, 864]], 'path1_seg2_2': [[70, 360], [90, 480], [110, 480], [110, 480]], 'path1_seg2_3': [[80, 360], [90, 480], [110, 480], [110, 480]], 'path1_seg3_1': [[30, 720], [40, 720], [50, 720], [50, 864]], 'path1_seg3_2': [[70, 480], [70, 720], [80, 720], [80, 720]], 'path1_seg3_3': [[80, 480], [100, 480], [120, 480], [90, 720]], 'path2_seg1_1': [[40, 720], [50, 720], [60, 720], [70, 720]], 'path2_seg1_2': [[70, 360], [90, 480], [80, 720], [90, 720]], 'path2_seg1_3': [[70, 360], [90, 480], [110, 480], [120, 480]], 'path2_seg2_1': [[40, 720], [60, 720], [70, 720], [80, 720]], 'path2_seg2_2': [[70, 360], [80, 480], [100, 480], [110, 480]], 'path2_seg2_3': [[80, 360], [100, 360], [100, 360], [120, 360]], 'path2_seg3_1': [[30, 720], [40, 720], [40, 1080], [50, 864]], 'path2_seg3_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path2_seg3_3': [[80, 360], [90, 480], [80, 720], [90, 720]], 'path3_seg1_1': [[60, 480], [80, 480], [80, 720], [80, 720]], 'path3_seg1_2': [[60, 480], [80, 480], [70, 720], [80, 720]], 'path3_seg1_3': [[90, 360], [100, 480], [120, 480], [120, 480]], 'path3_seg2_1': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path3_seg2_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path3_seg2_3': [[70, 360], [90, 480], [80, 720], [80, 720]], 'path3_seg3_1': [[60, 480], [60, 720], [70, 720], [80, 720]], 'path3_seg3_2': [[70, 360], [90, 480], [110, 480], [120, 480]], 'path3_seg3_3': [[70, 360], [80, 360], [90, 360], [100, 360]], 'path4_seg1_1': [[70, 480], [80, 720], [90, 720], [90, 720]], 'path4_seg1_2': [[80, 360], [80, 480], [90, 480], [100, 480]], 'path4_seg1_3': [[80, 360], [90, 480], [100, 480], [110, 480]], 'path4_seg2_1': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path4_seg2_2': [[80, 360], [100, 360], [90, 480], [100, 480]], 'path4_seg2_3': [[80, 360], [90, 480], [100, 480], [110, 480]], 'path4_seg3_1': [[80, 360], [100, 480], [110, 480], [110, 480]], 'path4_seg3_2': [[90, 360], [120, 360], [120, 360], [120, 360]], 'path4_seg3_3': [[100, 360], [110, 360], [110, 360], [120, 360]], 'path5_seg1_1': [[60, 480], [60, 720], [70, 720], [80, 720]], 'path5_seg1_2': [[60, 480], [60, 720], [80, 720], [80, 720]], 'path5_seg1_3': [[60, 480], [80, 720], [80, 720], [90, 720]], 'path5_seg2_1': [[70, 480], [70, 720], [80, 720], [80, 720]], 'path5_seg2_2': [[70, 480], [80, 720], [80, 720], [90, 720]], 'path5_seg2_3': [[70, 360], [90, 480], [120, 480], [120, 480]], 'path5_seg3_1': [[110, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg3_2': [[110, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg3_3': [[100, 360], [110, 360], [120, 360], [120, 360]]}
crytek_sponza_comb_drop_JOD = {'path1_seg1_1': [[40, 720], [60, 720], [60, 1080], [60, 1080]], 'path1_seg1_2': [[70, 480], [80, 480], [120, 480], [100, 720]], 'path1_seg1_3': [[70, 360], [80, 480], [90, 480], [100, 480]], 'path1_seg2_1': [[30, 720], [50, 720], [40, 1080], [40, 1080]], 'path1_seg2_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path1_seg2_3': [[70, 480], [80, 480], [80, 720], [90, 720]], 'path1_seg3_1': [[30, 720], [40, 720], [30, 1080], [40, 1080]], 'path1_seg3_2': [[50, 720], [60, 720], [60, 720], [70, 720]], 'path1_seg3_3': [[70, 480], [80, 720], [80, 720], [90, 720]], 'path2_seg1_1': [[30, 720], [30, 720], [40, 720], [40, 864]], 'path2_seg1_2': [[50, 480], [60, 720], [70, 720], [70, 720]], 'path2_seg1_3': [[50, 480], [70, 480], [70, 720], [80, 720]], 'path2_seg2_1': [[30, 720], [30, 720], [30, 1080], [30, 1080]], 'path2_seg2_2': [[40, 720], [50, 720], [50, 720], [60, 720]], 'path2_seg2_3': [[50, 480], [60, 720], [60, 720], [70, 720]], 'path2_seg3_1': [[30, 720], [30, 720], [40, 720], [40, 720]], 'path2_seg3_2': [[50, 480], [60, 720], [60, 720], [70, 720]], 'path2_seg3_3': [[50, 480], [80, 480], [80, 720], [80, 720]], 'path3_seg1_1': [[30, 720], [30, 720], [30, 720], [30, 864]], 'path3_seg1_2': [[50, 720], [60, 720], [70, 720], [70, 720]], 'path3_seg1_3': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path3_seg2_1': [[30, 720], [30, 720], [40, 720], [40, 720]], 'path3_seg2_2': [[50, 720], [50, 720], [60, 720], [60, 720]], 'path3_seg2_3': [[60, 720], [70, 720], [70, 720], [80, 720]], 'path3_seg3_1': [[30, 720], [40, 720], [40, 720], [40, 864]], 'path3_seg3_2': [[40, 720], [50, 720], [50, 720], [60, 720]], 'path3_seg3_3': [[50, 720], [60, 720], [60, 720], [70, 720]], 'path4_seg1_1': [[30, 720], [30, 720], [30, 864], [30, 864]], 'path4_seg1_2': [[30, 720], [30, 720], [30, 864], [40, 720]], 'path4_seg1_3': [[40, 720], [40, 720], [40, 720], [40, 720]], 'path4_seg2_1': [[30, 720], [30, 720], [30, 720], [30, 864]], 'path4_seg2_2': [[30, 720], [30, 720], [30, 720], [30, 864]], 'path4_seg2_3': [[30, 720], [40, 720], [40, 720], [40, 720]], 'path4_seg3_1': [[30, 720], [30, 864], [30, 1080], [30, 1080]], 'path4_seg3_2': [[30, 720], [30, 720], [40, 720], [40, 864]], 'path4_seg3_3': [[30, 720], [40, 720], [40, 720], [50, 720]], 'path5_seg1_1': [[30, 720], [30, 720], [40, 720], [40, 864]], 'path5_seg1_2': [[50, 480], [50, 720], [60, 720], [70, 720]], 'path5_seg1_3': [[50, 480], [80, 480], [70, 720], [70, 720]], 'path5_seg2_1': [[30, 720], [40, 720], [40, 720], [50, 720]], 'path5_seg2_2': [[60, 360], [80, 480], [70, 720], [80, 720]], 'path5_seg2_3': [[60, 360], [60, 480], [70, 480], [80, 480]], 'path5_seg3_1': [[40, 720], [50, 720], [50, 720], [60, 720]], 'path5_seg3_2': [[60, 480], [80, 480], [110, 480], [120, 480]], 'path5_seg3_3': [[80, 360], [100, 360], [80, 480], [110, 360]]}
gallery_comb_drop_JOD = {'path1_seg1_1': [[80, 480], [90, 720], [90, 720], [100, 720]], 'path1_seg1_2': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path1_seg1_3': [[110, 360], [120, 360], [120, 360], [120, 360]], 'path1_seg2_1': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path1_seg2_2': [[80, 480], [80, 720], [90, 720], [90, 720]], 'path1_seg2_3': [[90, 360], [80, 720], [90, 720], [100, 720]], 'path1_seg3_1': [[50, 720], [60, 720], [70, 720], [80, 720]], 'path1_seg3_2': [[60, 480], [80, 720], [80, 720], [90, 720]], 'path1_seg3_3': [[70, 480], [90, 480], [90, 720], [90, 720]], 'path2_seg1_1': [[30, 720], [40, 720], [50, 864], [60, 864]], 'path2_seg1_2': [[60, 480], [70, 720], [80, 720], [90, 720]], 'path2_seg1_3': [[70, 360], [90, 480], [110, 480], [120, 480]], 'path2_seg2_1': [[50, 480], [50, 720], [50, 864], [70, 720]], 'path2_seg2_2': [[60, 360], [80, 480], [80, 720], [80, 720]], 'path2_seg2_3': [[60, 360], [80, 360], [90, 480], [110, 480]], 'path2_seg3_1': [[110, 360], [110, 480], [110, 480], [110, 480]], 'path2_seg3_2': [[90, 360], [90, 480], [110, 480], [120, 480]], 'path2_seg3_3': [[80, 360], [100, 360], [120, 360], [100, 480]], 'path3_seg1_1': [[50, 480], [70, 480], [90, 480], [110, 480]], 'path3_seg1_2': [[80, 480], [110, 480], [110, 480], [110, 480]], 'path3_seg1_3': [[110, 360], [120, 360], [120, 360], [120, 360]], 'path3_seg2_1': [[40, 720], [50, 720], [50, 720], [60, 720]], 'path3_seg2_2': [[60, 480], [60, 720], [70, 720], [70, 720]], 'path3_seg2_3': [[60, 480], [70, 720], [70, 720], [80, 720]], 'path3_seg3_1': [[30, 720], [40, 864], [50, 864], [60, 864]], 'path3_seg3_2': [[60, 480], [60, 720], [70, 720], [70, 720]], 'path3_seg3_3': [[70, 360], [90, 480], [80, 720], [80, 720]], 'path4_seg1_1': [[50, 480], [50, 720], [60, 720], [60, 720]], 'path4_seg1_2': [[70, 480], [70, 720], [80, 720], [80, 720]], 'path4_seg1_3': [[90, 360], [100, 480], [110, 480], [120, 480]], 'path4_seg2_1': [[80, 360], [120, 360], [110, 480], [110, 480]], 'path4_seg2_2': [[90, 360], [110, 360], [120, 360], [120, 360]], 'path4_seg2_3': [[80, 360], [100, 360], [110, 360], [110, 360]], 'path4_seg3_1': [[50, 480], [50, 720], [60, 720], [60, 720]], 'path4_seg3_2': [[80, 360], [90, 480], [100, 480], [110, 480]], 'path4_seg3_3': [[90, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg1_1': [[80, 480], [90, 720], [90, 720], [100, 720]], 'path5_seg1_2': [[90, 480], [110, 480], [120, 480], [120, 480]], 'path5_seg1_3': [[110, 360], [120, 480], [120, 480], [120, 480]], 'path5_seg2_1': [[60, 480], [60, 720], [60, 720], [70, 720]], 'path5_seg2_2': [[70, 480], [70, 720], [70, 720], [80, 720]], 'path5_seg2_3': [[100, 360], [100, 480], [120, 480], [120, 480]], 'path5_seg3_1': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path5_seg3_2': [[80, 360], [80, 480], [110, 480], [120, 480]], 'path5_seg3_3': [[80, 360], [90, 480], [110, 480], [110, 480]]}
living_room_comb_drop_JOD = {'path1_seg1_1': [[80, 720], [80, 720], [80, 720], [90, 720]], 'path1_seg1_2': [[100, 480], [110, 480], [110, 480], [110, 480]], 'path1_seg1_3': [[100, 360], [120, 360], [120, 360], [120, 360]], 'path1_seg2_1': [[70, 480], [80, 720], [80, 720], [80, 720]], 'path1_seg2_2': [[110, 480], [120, 480], [110, 720], [110, 720]], 'path1_seg2_3': [[120, 360], [120, 360], [120, 360], [120, 360]], 'path1_seg3_1': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path1_seg3_2': [[80, 720], [90, 720], [100, 720], [100, 720]], 'path1_seg3_3': [[100, 720], [100, 720], [100, 720], [100, 720]], 'path2_seg1_1': [[60, 720], [80, 720], [80, 720], [80, 720]], 'path2_seg1_2': [[70, 720], [80, 720], [90, 720], [90, 720]], 'path2_seg1_3': [[70, 720], [80, 720], [80, 720], [80, 720]], 'path2_seg2_1': [[80, 480], [80, 720], [80, 720], [80, 720]], 'path2_seg2_2': [[110, 360], [110, 480], [110, 480], [110, 480]], 'path2_seg2_3': [[120, 360], [120, 360], [120, 360], [120, 360]], 'path2_seg3_1': [[70, 720], [80, 720], [80, 720], [90, 720]], 'path2_seg3_2': [[100, 480], [100, 720], [100, 720], [100, 720]], 'path2_seg3_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path3_seg1_1': [[90, 480], [80, 720], [80, 720], [80, 720]], 'path3_seg1_2': [[90, 720], [100, 720], [100, 720], [100, 720]], 'path3_seg1_3': [[90, 480], [120, 480], [120, 480], [120, 480]], 'path3_seg2_1': [[80, 480], [80, 720], [80, 720], [80, 720]], 'path3_seg2_2': [[110, 360], [110, 360], [110, 360], [120, 360]], 'path3_seg2_3': [[120, 360], [120, 360], [120, 360], [120, 360]], 'path3_seg3_1': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path3_seg3_2': [[80, 480], [80, 720], [90, 720], [90, 720]], 'path3_seg3_3': [[110, 360], [110, 360], [110, 360], [110, 360]], 'path4_seg1_1': [[70, 720], [80, 720], [80, 720], [80, 720]], 'path4_seg1_2': [[70, 480], [80, 720], [90, 720], [90, 720]], 'path4_seg1_3': [[120, 360], [120, 360], [120, 360], [120, 360]], 'path4_seg2_1': [[40, 720], [50, 720], [70, 720], [60, 864]], 'path4_seg2_2': [[80, 480], [90, 720], [90, 720], [100, 720]], 'path4_seg2_3': [[90, 360], [110, 360], [110, 480], [110, 480]], 'path4_seg3_1': [[50, 720], [60, 720], [70, 720], [80, 864]], 'path4_seg3_2': [[80, 480], [90, 720], [90, 720], [90, 720]], 'path4_seg3_3': [[110, 360], [110, 480], [110, 480], [110, 480]], 'path5_seg1_1': [[50, 720], [60, 720], [70, 720], [70, 720]], 'path5_seg1_2': [[90, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg1_3': [[110, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg2_1': [[50, 720], [70, 720], [70, 720], [80, 720]], 'path5_seg2_2': [[90, 360], [120, 360], [120, 360], [120, 360]], 'path5_seg2_3': [[100, 360], [110, 360], [120, 360], [120, 360]], 'path5_seg3_1': [[70, 480], [110, 480], [80, 720], [80, 720]], 'path5_seg3_2': [[90, 360], [110, 360], [120, 360], [120, 360]], 'path5_seg3_3': [[110, 360], [120, 360], [120, 360], [120, 360]]}
lost_empire_comb_drop_JOD = {'path1_seg1_1': [[30, 720], [40, 720], [50, 720], [50, 720]], 'path1_seg1_2': [[50, 720], [60, 720], [60, 720], [70, 720]], 'path1_seg1_3': [[110, 480], [100, 720], [110, 720], [110, 720]], 'path1_seg2_1': [[80, 480], [70, 720], [80, 720], [90, 720]], 'path1_seg2_2': [[80, 360], [110, 480], [120, 480], [120, 480]], 'path1_seg2_3': [[90, 360], [110, 360], [120, 360], [120, 360]], 'path1_seg3_1': [[80, 480], [80, 720], [80, 720], [90, 720]], 'path1_seg3_2': [[80, 480], [110, 480], [120, 480], [120, 480]], 'path1_seg3_3': [[90, 360], [90, 480], [110, 480], [120, 480]], 'path2_seg1_1': [[50, 480], [60, 720], [70, 720], [80, 720]], 'path2_seg1_2': [[80, 360], [100, 480], [110, 480], [120, 480]], 'path2_seg1_3': [[90, 360], [120, 360], [120, 480], [120, 480]], 'path2_seg2_1': [[50, 480], [60, 720], [70, 720], [80, 720]], 'path2_seg2_2': [[80, 360], [100, 480], [120, 480], [100, 720]], 'path2_seg2_3': [[90, 360], [100, 480], [120, 480], [120, 480]], 'path2_seg3_1': [[50, 480], [60, 720], [70, 720], [80, 720]], 'path2_seg3_2': [[80, 360], [100, 480], [120, 480], [100, 720]], 'path2_seg3_3': [[90, 360], [100, 480], [120, 480], [120, 480]], 'path3_seg1_1': [[70, 480], [80, 720], [80, 720], [90, 720]], 'path3_seg1_2': [[70, 480], [80, 720], [80, 720], [90, 720]], 'path3_seg1_3': [[70, 360], [100, 480], [90, 720], [90, 720]], 'path3_seg2_1': [[50, 480], [50, 864], [70, 720], [70, 720]], 'path3_seg2_2': [[60, 480], [60, 720], [70, 720], [80, 720]], 'path3_seg2_3': [[80, 480], [110, 480], [110, 480], [110, 720]], 'path3_seg3_1': [[30, 720], [40, 720], [40, 1080], [50, 864]], 'path3_seg3_2': [[30, 720], [40, 720], [40, 1080], [50, 864]], 'path3_seg3_3': [[60, 480], [110, 480], [90, 720], [90, 720]], 'path4_seg1_1': [[40, 480], [40, 720], [50, 720], [60, 720]], 'path4_seg1_2': [[40, 720], [60, 720], [60, 720], [70, 720]], 'path4_seg1_3': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path4_seg2_1': [[50, 480], [50, 720], [60, 720], [70, 720]], 'path4_seg2_2': [[40, 720], [60, 720], [60, 720], [70, 720]], 'path4_seg2_3': [[60, 480], [90, 480], [80, 720], [80, 720]], 'path4_seg3_1': [[50, 480], [50, 720], [60, 720], [70, 720]], 'path4_seg3_2': [[50, 480], [60, 720], [70, 720], [80, 720]], 'path4_seg3_3': [[90, 360], [100, 480], [120, 480], [100, 720]], 'path5_seg1_1': [[60, 480], [80, 480], [80, 720], [80, 720]], 'path5_seg1_2': [[60, 480], [80, 480], [100, 480], [110, 480]], 'path5_seg1_3': [[70, 360], [100, 360], [120, 360], [100, 480]], 'path5_seg2_1': [[50, 480], [60, 720], [70, 720], [70, 720]], 'path5_seg2_2': [[70, 360], [90, 480], [120, 480], [90, 720]], 'path5_seg2_3': [[80, 360], [90, 360], [110, 360], [120, 360]], 'path5_seg3_1': [[90, 360], [110, 360], [110, 360], [120, 360]], 'path5_seg3_2': [[80, 360], [100, 360], [110, 360], [110, 360]], 'path5_seg3_3': [[80, 360], [90, 360], [100, 360], [110, 360]]}
room_comb_drop_JOD = {'path1_seg1_1': [[50, 720], [60, 720], [70, 720], [70, 720]], 'path1_seg1_2': [[80, 480], [80, 720], [90, 720], [100, 720]], 'path1_seg1_3': [[110, 360], [110, 480], [110, 480], [120, 480]], 'path1_seg2_1': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path1_seg2_2': [[80, 480], [80, 720], [90, 720], [90, 720]], 'path1_seg2_3': [[100, 360], [110, 360], [110, 360], [110, 360]], 'path1_seg3_1': [[100, 360], [100, 360], [100, 360], [100, 360]], 'path1_seg3_2': [[120, 360], [120, 360], [120, 360], [120, 360]], 'path1_seg3_3': [[110, 360], [110, 360], [120, 360], [120, 360]], 'path2_seg1_1': [[50, 720], [60, 720], [70, 720], [70, 720]], 'path2_seg1_2': [[50, 720], [70, 720], [70, 720], [80, 720]], 'path2_seg1_3': [[90, 480], [80, 720], [80, 720], [90, 720]], 'path2_seg2_1': [[60, 720], [70, 720], [70, 720], [80, 720]], 'path2_seg2_2': [[90, 480], [80, 720], [80, 720], [80, 720]], 'path2_seg2_3': [[110, 360], [110, 360], [110, 360], [110, 360]], 'path2_seg3_1': [[40, 720], [50, 720], [50, 720], [60, 720]], 'path2_seg3_2': [[40, 720], [50, 720], [70, 720], [70, 720]], 'path2_seg3_3': [[80, 360], [110, 360], [100, 480], [110, 480]], 'path3_seg1_1': [[40, 720], [40, 720], [50, 720], [50, 720]], 'path3_seg1_2': [[60, 720], [80, 720], [80, 720], [80, 720]], 'path3_seg1_3': [[70, 720], [80, 720], [80, 720], [80, 720]], 'path3_seg2_1': [[50, 720], [60, 720], [70, 720], [70, 720]], 'path3_seg2_2': [[120, 360], [110, 480], [110, 480], [110, 480]], 'path3_seg2_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path3_seg3_1': [[80, 480], [80, 720], [90, 720], [90, 720]], 'path3_seg3_2': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path3_seg3_3': [[80, 720], [80, 720], [100, 720], [100, 720]], 'path4_seg1_1': [[110, 360], [110, 480], [110, 480], [110, 480]], 'path4_seg1_2': [[80, 360], [90, 360], [90, 360], [100, 360]], 'path4_seg1_3': [[100, 360], [120, 360], [120, 360], [120, 360]], 'path4_seg2_1': [[100, 360], [100, 480], [120, 480], [120, 480]], 'path4_seg2_2': [[110, 360], [120, 360], [120, 360], [120, 360]], 'path4_seg2_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path4_seg3_1': [[60, 720], [80, 720], [80, 720], [80, 720]], 'path4_seg3_2': [[110, 480], [120, 480], [120, 480], [120, 480]], 'path4_seg3_3': [[120, 480], [100, 720], [100, 720], [100, 720]], 'path5_seg1_1': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path5_seg1_2': [[100, 480], [120, 480], [100, 720], [100, 720]], 'path5_seg1_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path5_seg2_1': [[110, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg2_2': [[110, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg2_3': [[100, 360], [110, 360], [110, 360], [120, 360]], 'path5_seg3_1': [[50, 720], [60, 720], [70, 720], [80, 720]], 'path5_seg3_2': [[70, 720], [90, 720], [90, 720], [90, 720]], 'path5_seg3_3': [[120, 480], [110, 720], [110, 720], [110, 720]]}
suntemple_comb_drop_JOD = {'path1_seg1_1': [[40, 720], [40, 720], [50, 720], [50, 720]], 'path1_seg1_2': [[40, 720], [50, 720], [50, 720], [60, 720]], 'path1_seg1_3': [[60, 480], [60, 720], [70, 720], [80, 720]], 'path1_seg2_1': [[30, 720], [40, 720], [50, 720], [50, 720]], 'path1_seg2_2': [[40, 720], [50, 720], [60, 720], [60, 720]], 'path1_seg2_3': [[70, 480], [90, 480], [100, 480], [100, 480]], 'path1_seg3_1': [[40, 720], [50, 720], [50, 720], [50, 720]], 'path1_seg3_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path1_seg3_3': [[80, 360], [90, 480], [90, 480], [90, 480]], 'path2_seg1_1': [[30, 720], [40, 720], [40, 720], [40, 720]], 'path2_seg1_2': [[50, 480], [80, 480], [70, 720], [80, 720]], 'path2_seg1_3': [[60, 480], [80, 480], [90, 480], [110, 480]], 'path2_seg2_1': [[30, 720], [40, 720], [50, 720], [50, 720]], 'path2_seg2_2': [[70, 360], [80, 480], [100, 480], [110, 480]], 'path2_seg2_3': [[90, 360], [110, 360], [120, 360], [120, 360]], 'path2_seg3_1': [[40, 720], [50, 720], [60, 720], [60, 720]], 'path2_seg3_2': [[50, 480], [80, 480], [80, 720], [80, 720]], 'path2_seg3_3': [[70, 360], [90, 480], [100, 480], [100, 480]], 'path3_seg1_1': [[70, 480], [70, 720], [80, 720], [80, 720]], 'path3_seg1_2': [[80, 360], [100, 480], [110, 480], [110, 480]], 'path3_seg1_3': [[50, 360], [60, 480], [70, 480], [80, 480]], 'path3_seg2_1': [[60, 480], [60, 720], [60, 720], [60, 720]], 'path3_seg2_2': [[60, 480], [60, 720], [70, 720], [80, 720]], 'path3_seg2_3': [[70, 480], [70, 720], [80, 720], [80, 720]], 'path3_seg3_1': [[50, 480], [60, 480], [60, 720], [60, 720]], 'path3_seg3_2': [[50, 480], [60, 480], [80, 480], [70, 720]], 'path3_seg3_3': [[80, 360], [80, 480], [100, 480], [110, 480]], 'path4_seg1_1': [[50, 720], [60, 720], [60, 720], [70, 720]], 'path4_seg1_2': [[70, 360], [80, 480], [90, 480], [80, 720]], 'path4_seg1_3': [[60, 360], [70, 480], [80, 480], [100, 480]], 'path4_seg2_1': [[40, 480], [30, 720], [40, 720], [40, 720]], 'path4_seg2_2': [[40, 480], [50, 720], [50, 720], [60, 720]], 'path4_seg2_3': [[50, 360], [80, 360], [80, 480], [90, 480]], 'path4_seg3_1': [[40, 720], [50, 720], [60, 720], [60, 720]], 'path4_seg3_2': [[60, 720], [60, 720], [70, 720], [80, 720]], 'path4_seg3_3': [[70, 480], [70, 720], [80, 720], [80, 720]], 'path5_seg1_1': [[60, 720], [100, 720], [110, 720], [110, 720]], 'path5_seg1_2': [[110, 480], [100, 720], [110, 720], [120, 720]], 'path5_seg1_3': [[110, 360], [120, 480], [120, 480], [120, 480]], 'path5_seg2_1': [[80, 360], [110, 480], [80, 720], [80, 720]], 'path5_seg2_2': [[80, 360], [80, 480], [90, 480], [90, 480]], 'path5_seg2_3': [[120, 360], [120, 360], [120, 480], [120, 480]], 'path5_seg3_1': [[90, 360], [90, 480], [110, 480], [110, 480]], 'path5_seg3_2': [[80, 360], [110, 360], [110, 480], [110, 480]], 'path5_seg3_3': [[80, 480], [110, 480], [110, 480], [110, 480]]}
sibenik_comb_drop_JOD = {'path1_seg1_1': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path1_seg1_2': [[80, 480], [90, 720], [100, 720], [100, 720]], 'path1_seg1_3': [[100, 360], [120, 480], [100, 720], [110, 720]], 'path1_seg2_1': [[70, 480], [80, 720], [80, 720], [90, 720]], 'path1_seg2_2': [[80, 360], [110, 480], [100, 720], [100, 720]], 'path1_seg2_3': [[90, 360], [100, 480], [120, 480], [120, 480]], 'path1_seg3_1': [[40, 720], [50, 720], [60, 720], [80, 720]], 'path1_seg3_2': [[70, 480], [100, 480], [90, 720], [90, 720]], 'path1_seg3_3': [[90, 360], [100, 480], [110, 480], [120, 480]], 'path2_seg1_1': [[30, 720], [50, 720], [40, 1080], [60, 864]], 'path2_seg1_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path2_seg1_3': [[80, 360], [100, 480], [120, 480], [100, 720]], 'path2_seg2_1': [[30, 720], [40, 720], [50, 720], [60, 864]], 'path2_seg2_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path2_seg2_3': [[80, 360], [110, 360], [110, 480], [120, 480]], 'path2_seg3_1': [[50, 480], [60, 720], [70, 720], [80, 720]], 'path2_seg3_2': [[70, 360], [80, 480], [80, 720], [90, 720]], 'path2_seg3_3': [[70, 360], [80, 480], [80, 720], [80, 720]], 'path3_seg1_1': [[40, 720], [50, 720], [70, 720], [70, 864]], 'path3_seg1_2': [[70, 360], [70, 720], [80, 720], [90, 720]], 'path3_seg1_3': [[70, 360], [90, 480], [90, 720], [90, 720]], 'path3_seg2_1': [[40, 720], [50, 720], [60, 720], [70, 720]], 'path3_seg2_2': [[50, 480], [70, 720], [80, 720], [80, 720]], 'path3_seg2_3': [[70, 360], [100, 480], [120, 480], [100, 720]], 'path3_seg3_1': [[60, 480], [70, 720], [70, 720], [80, 720]], 'path3_seg3_2': [[80, 360], [100, 360], [120, 360], [110, 480]], 'path3_seg3_3': [[90, 360], [100, 360], [110, 360], [110, 360]], 'path4_seg1_1': [[90, 480], [90, 720], [90, 720], [90, 720]], 'path4_seg1_2': [[70, 480], [80, 720], [90, 720], [100, 720]], 'path4_seg1_3': [[120, 360], [120, 480], [120, 480], [120, 480]], 'path4_seg2_1': [[90, 360], [100, 360], [110, 360], [110, 360]], 'path4_seg2_2': [[100, 360], [120, 360], [120, 360], [120, 360]], 'path4_seg2_3': [[100, 360], [110, 360], [110, 360], [110, 360]], 'path4_seg3_1': [[50, 480], [70, 720], [80, 720], [80, 720]], 'path4_seg3_2': [[90, 360], [110, 360], [110, 360], [110, 360]], 'path4_seg3_3': [[100, 360], [110, 360], [110, 360], [110, 360]], 'path5_seg1_1': [[60, 720], [70, 720], [70, 720], [80, 720]], 'path5_seg1_2': [[80, 480], [80, 720], [90, 720], [100, 720]], 'path5_seg1_3': [[90, 480], [110, 480], [110, 720], [110, 720]], 'path5_seg2_1': [[40, 720], [40, 720], [50, 720], [60, 720]], 'path5_seg2_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path5_seg2_3': [[80, 360], [90, 480], [120, 480], [100, 720]], 'path5_seg3_1': [[60, 480], [70, 720], [80, 720], [90, 720]], 'path5_seg3_2': [[80, 360], [110, 360], [110, 480], [110, 480]], 'path5_seg3_3': [[100, 360], [120, 360], [120, 360], [120, 360]]}
suntemple_statue_comb_drop_JOD = {'path1_seg1_1': [[70, 360], [80, 480], [80, 720], [120, 720]], 'path1_seg1_2': [[110, 360], [110, 480], [120, 480], [120, 480]], 'path1_seg1_3': [[110, 360], [120, 360], [110, 480], [110, 480]], 'path1_seg2_1': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path1_seg2_2': [[100, 480], [80, 720], [90, 720], [100, 720]], 'path1_seg2_3': [[110, 480], [100, 720], [100, 720], [100, 720]], 'path1_seg3_1': [[30, 864], [40, 1080], [60, 864], [50, 1080]], 'path1_seg3_2': [[60, 720], [80, 720], [80, 720], [90, 720]], 'path1_seg3_3': [[80, 480], [120, 480], [100, 720], [100, 720]], 'path2_seg1_1': [[40, 720], [40, 720], [50, 864], [60, 864]], 'path2_seg1_2': [[80, 360], [90, 480], [110, 480], [120, 480]], 'path2_seg1_3': [[90, 360], [110, 360], [90, 480], [100, 480]], 'path2_seg2_1': [[40, 720], [50, 720], [50, 864], [60, 864]], 'path2_seg2_2': [[90, 360], [110, 480], [120, 480], [90, 720]], 'path2_seg2_3': [[80, 360], [90, 480], [110, 480], [110, 480]], 'path2_seg3_1': [[60, 720], [80, 720], [80, 720], [80, 720]], 'path2_seg3_2': [[80, 480], [110, 480], [90, 720], [90, 720]], 'path2_seg3_3': [[100, 360], [110, 480], [120, 480], [120, 480]], 'path3_seg1_1': [[30, 720], [40, 864], [40, 1080], [60, 864]], 'path3_seg1_2': [[60, 480], [70, 720], [80, 720], [80, 720]], 'path3_seg1_3': [[80, 360], [80, 480], [80, 720], [90, 720]], 'path3_seg2_1': [[60, 720], [70, 720], [80, 720], [80, 720]], 'path3_seg2_2': [[50, 720], [70, 720], [80, 720], [80, 864]], 'path3_seg2_3': [[70, 480], [80, 720], [80, 720], [80, 720]], 'path3_seg3_1': [[40, 720], [50, 720], [70, 720], [70, 864]], 'path3_seg3_2': [[70, 480], [80, 720], [80, 720], [90, 720]], 'path3_seg3_3': [[80, 360], [120, 480], [110, 720], [110, 720]], 'path4_seg1_1': [[60, 720], [80, 720], [80, 720], [90, 720]], 'path4_seg1_2': [[90, 480], [120, 480], [100, 720], [100, 720]], 'path4_seg1_3': [[80, 360], [90, 360], [90, 480], [90, 480]], 'path4_seg2_1': [[90, 480], [110, 720], [110, 720], [110, 720]], 'path4_seg2_2': [[70, 480], [80, 720], [90, 720], [90, 720]], 'path4_seg2_3': [[90, 480], [80, 720], [90, 720], [90, 720]], 'path4_seg3_1': [[30, 720], [40, 1080], [40, 1080], [50, 1080]], 'path4_seg3_2': [[40, 720], [60, 864], [60, 1080], [70, 1080]], 'path4_seg3_3': [[70, 720], [90, 720], [100, 720], [100, 720]], 'path5_seg1_1': [[30, 864], [40, 1080], [50, 1080], [50, 1080]], 'path5_seg1_2': [[120, 480], [100, 720], [110, 720], [110, 720]], 'path5_seg1_3': [[110, 360], [120, 360], [110, 480], [110, 480]], 'path5_seg2_1': [[40, 720], [50, 864], [60, 864], [60, 864]], 'path5_seg2_2': [[80, 480], [90, 720], [90, 720], [100, 720]], 'path5_seg2_3': [[80, 360], [100, 480], [110, 480], [110, 480]], 'path5_seg3_1': [[50, 720], [60, 720], [70, 720], [70, 720]], 'path5_seg3_2': [[80, 480], [110, 480], [100, 720], [100, 720]], 'path5_seg3_3': [[90, 480], [120, 480], [120, 480], [120, 480]]}

drop_JOD_dicts = {
        'bedroom': bedroom_comb_drop_JOD,
        'bistro': bistro_comb_drop_JOD,
        'crytek_sponza': crytek_sponza_comb_drop_JOD,
        'gallery': gallery_comb_drop_JOD,
        'living_room': living_room_comb_drop_JOD,
        'lost_empire': lost_empire_comb_drop_JOD,
        'room': room_comb_drop_JOD,
        'sibenik': sibenik_comb_drop_JOD,
        'suntemple': suntemple_comb_drop_JOD,
        'suntemple_statue': suntemple_statue_comb_drop_JOD
    }

# JODs4000 = [4.647, 4.867, 4.954, 5.007, 5.056, 4.748, 4.956, 5.026, 5.089, 5.158, 5.043, 5.299, 5.394, 5.452, 5.503,]
# JODs8000 = [4.799, 5.03, 5.137, 5.198, 5.253, 5.265, 5.529, 5.669, 5.732, 5.793, 5.801, 6.108, 6.237, 6.333, 6.439,]
# for JOD in [5.394, 5.452, 5.043, 5.299, 5.503, 5.089, 44.748, 4.956, 5.026, 5.158]:
# for JOD in [4.725, 4.417, 4.519, 4.707, 4.708]:
# for JOD in [4.558, 4.631, 4.773, 4.822, 4.906]:
# for JOD in [4.699, 4.815, 4.944, 4.958, 4.983]:
# for JOD in [4.868, 4.993, 5.24, 5.196, 5.285]:
# for JOD in [5.57, 5.66, 5.286, 5.383, 5.607]:




# 4000 1080 864 720 480 360
# fps60,  7.4184, 7.3124, 7.1115, 6.9, 6.7021,
# fps70,  7.6549, 7.5675, 7.4122, 7.2358, 7.0402,
# fps80,  7.8837, 7.7779, 7.6665, 7.4091, 7.1709,
# fps90,  7.8403, 7.7722, 7.7039, 7.5186, 7.2843,
# fps100, 7.8066, 7.8162, 7.7529, 7.5565, 7.3289,
# fps110, 7.7734, 7.7273, 7.7162, 7.5713, 7.3707,
# fps120, 7.7309, 7.8129, 7.7026, 7.5979, 7.3579,



# 8000
# fps60     7.596, 7.4356, 7.2372, 7.0347, 6.8394,
# fps70     7.9234, 7.817, 7.623, 7.4477, 7.2221,
# fps80     8.2735, 8.1333, 7.8972, 7.6778, 7.3922,
# fps90     8.2045, 8.0959, 7.9976, 7.8333, 7.5588,
# fps100    8.2471, 8.1898, 8.1053, 7.9108, 7.6091,
# fps110    8.2707, 8.1953, 8.1378, 7.9737, 7.6955,
# fps120    8.3032, 8.2869, 8.2404, 7.9828, 7.7041,



# 16000
# fps60     7.6625, 7.4908, 7.3033, 7.1097, 6.8946,
# fps70     7.9977, 7.8477, 7.6857, 7.5487, 7.3069,
# fps80     8.4064, 8.2019, 8.0356, 7.826, 7.5003,
# fps90     8.3785, 8.2581, 8.1676, 8.0099, 7.6935,
# fps100    8.4336, 8.3571, 8.2841, 8.1011, 7.7656,
# fps110    8.4963, 8.4375, 8.3957, 8.2071, 7.8642,
# fps120    8.5779, 8.5041, 8.4824, 8.2624, 7.9056,