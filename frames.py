import os
import glob
import shutil
import subprocess
import numpy as np
import argparse
import patches
from utils import *
from datetime import datetime

def move_images(parent_dir, folder_name):
    new_folder_path = os.path.join(parent_dir, folder_name)
    print(f'new_folder_path \n {new_folder_path}')

def main(bitrate, resolution):
    # Your processing logic here
    print(f"Processing video with bitrate: {bitrate} and resolution: {resolution}\n")

# rename folders of frames so they can be used for training
if __name__ == "__main__":
    print(patches.__file__)

    # basePath = 'C:/Users/15142/source/repos/Falcor/Falcor/build/Source/PerceptualRendering/EncodeDecode'
    # basePath = 'C:/Users/15142/new/Falcor/build/windows-vs2022/Source/Samples/EncodeDecode'
    basePath = 'C:/Users/15142/new/Falcor/Source/Samples/EncodeDecode/'
    # basePath = 'D:/VRR-frame/room-normal'

    refOutputDir = f'{basePath}/refOutputBMP'
    decOutputDir = f'{basePath}/decOutputBMP'

    # VRRMP4DIR = 'C:/Users/15142/Desktop/VRRMP4'
    # imageOutput = 'C:/Users/15142/Desktop/VRR_CVVDP_Image'
    CVVDPDIR = 'C:/Users/15142/Projects/ColorVideoVDP/ColorVideoVDP'
    input_pattern = "%d.bmp"

    print(f'\n\nTrigger python file successfully')

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('bitrate', type=str, help='The bitrate of the video')
    parser.add_argument('resolution', type=str, help='The resolution of the video')
    parser.add_argument('framerate', type=str, help='The resolution of the video')
    parser.add_argument('scene', type=str, help='Scene name')
    parser.add_argument('speed', type=str, help='Speed value')
    args = parser.parse_args()
    # main(args.bitrate, args.resolution)
    size = args.resolution
    bitrate = args.bitrate
    framerate = args.framerate
    scene = args.scene
    speed = args.speed

    # size = 360
    # bitrate = 3000
    # framerate = 60

    print(f"Processing frames with bitrate: {bitrate}, framerate {framerate} and resolution: {size}\n")


    GETREF = True # True False
    GETDEC = False
    DARKSETTING = False
    num_delete = 4


    if GETREF:
        # total_ref_files = len(os.listdir(refOutputDir)) # Count the number of files
        # print(f'total_ref_files {total_ref_files}')
        # refDeleteFiles = []
        # for i in range(1, num_delete+1):
        #     refDeleteFiles.append(f"{total_ref_files-i}.bmp")
        
        # for i in range(0, num_delete):
        #     refDeleteFiles.append(f"{i}.bmp")

        # delete_files(refOutputDir, refDeleteFiles)
        
        # new_fps_path = os.path.join(basePath, f'fps{framerate}')
        # os.makedirs(new_fps_path, exist_ok=True)
        # print(f'new_fps_path \n {new_fps_path}')

        folder_name = f'{scene}_{speed}_ref{framerate}_{size}_{bitrate}'

        new_folder_path = os.path.join(basePath, folder_name)
        if not os.path.exists(new_folder_path):
            os.rename(refOutputDir, new_folder_path)
            os.makedirs(refOutputDir)
            print(f'rename to {new_folder_path}')


    if GETDEC:
        # decDeleteFiles = []
        # for i in range(0, num_delete):
        #     decDeleteFiles.append(f"{i}.bmp")
        # delete_files(decOutputDir, decDeleteFiles)

        folder_name = f'{framerate}_{size}_{bitrate}'

        new_fps_path = os.path.join(basePath, f'{bitrate}bps', f'fps{framerate}')
        os.makedirs(new_fps_path, exist_ok=True)

        new_folder_path = os.path.join(new_fps_path, folder_name)
        print(f'rename to {new_folder_path}')
        if not os.path.exists(new_folder_path):
            os.rename(decOutputDir, new_folder_path)
            print(f'rename successfully')
            os.makedirs(decOutputDir)

        # move_images(imageOutput, folder_name)
        # runCVVDP(newRefPath, newDecPath)

    
    DELETEBMP = False # True False
    if DELETEBMP:
        emptyFolder(refOutputDir, deleteBMP=DELETEBMP)
        emptyFolder(decOutputDir, deleteBMP=DELETEBMP)

