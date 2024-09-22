import os
import numpy as np
import math
from PIL import Image
from utils import *
import torch
import torchvision.transforms as transforms
import datetime
import secrets
import pandas as pd



def get_jod_score(all_data, sheet_name, bitrate, fps, resolution):
    """
    Retrieves a JOD score from the nested dictionary using the specified sheet name, bitrate, fps, and resolution.
    Returns 'Not Found' if any key is missing.
    """
    return all_data.get(sheet_name, {}).get(bitrate, {}).get(fps, {}).get(resolution, "Not Found")


def add_data(bitrate, fps, resolutions, jod_scores):
    if bitrate not in data:
        data[bitrate] = {}
    if fps not in data[bitrate]:
        data[bitrate][fps] = {}
    for res, score in zip(resolutions, jod_scores):
        data[bitrate][fps][res] = score
    return data

def type2(df, label_idx, bitrate, number, refresh_rate, SAVE = False):
    """x axis is resolution, y axis is JOD, color is bitrate, labels are refresh rate"""
    for num in range(number): # loop column
        # cvvdp jod from file1
        jod_cvvdp = df.iloc[label_idx, 1+5*num:6+5*num].values
        jod_cvvdp = [float(v) for v in jod_cvvdp]        

        # print(f'idx {num}, fps{refresh_rate[num]}, JOD {jod_cvvdp}, ') # max JOD {max(jod_cvvdp)}
        data = add_data(bitrate, refresh_rate[num], ['360', '480', '720', '864', '1080'], jod_cvvdp)
    return data




# def find_jod(df, bitrate_row_idx, fps, resolution_idx):
def find_jod(df):
    # num = int(fps/10 - 3)
    # jod_cvvdp = df.iloc[bitrate_row_idx, 1+5*num:6+5*num].values # 1080 to 360
    # # print(f'cvvdp {jod_cvvdp}, output {jod_cvvdp[resolution_idx]}')
    # return jod_cvvdp[resolution_idx]
    print(f'df {df.columns}')
    print(f'df \n {df}')
    df.columns = [f'{col[1]}_fps{col[0]}' if 'bitrate' not in col else col[1] for col in df.columns]
    # print(df)

    # Initialize a dictionary to hold the data for quick lookup
    data_dict = {}

    # Iterate over rows to populate the dictionary
    for index, row in df.iterrows():
        bitrate = row['bitrate']
        print(f'bitrate {bitrate}')
        # for col in df.columns:
        #     if col != 'bitrate':
        #         fps, res = col.split('_')
        #         res = int(res[3:])  # Convert 'fps30' to 30, '360' from 'JOD_360'
        #         fps = int(fps[3:])
        #         # Use tuple (bitrate, fps, resolution) as key
        #         data_dict[(bitrate, fps, res)] = row[col]








# find JOD value during validation/test stage
if __name__ == "__main__":
    scene_arr = [
            'suntemple_statue',
            #  'crytek_sponza', 'gallery', 
            #  'living_room', 'lost_empire', 
            #  'room', 'sibenik', 'suntemple', 
            #  'suntemple_statue'
            ]
    bitrates = [500, 1000, 1500, 2000]
    DEBUG = False

    bitrate_dict = {500: 0, 1000: 1, 1500: 2, 2000: 3}
    resolution_dict = {1080: 0, 864: 1, 720: 2, 480: 3, 360: 4}

    for scene in scene_arr:
        all_data = {}
        print(f'========== scene {scene} ==========')
        file_path = f'{CVVDP_EXCEL}/{scene}.xlsx'
        for path in range(1, 6):
            for seg in range(1, 4):
                for speed in range(1, 4):
                    data = {}
                    for bitrate in bitrates:
                        sheet_name = f'path{path}_seg{seg}_{speed}'
                        # print(f'sheet_name {sheet_name}')
                        df = pd.read_excel(file_path, sheet_name=sheet_name, na_values=['NA'])
                        # jod = find_jod(df)
                        data = type2(df, bitrate_dict[bitrate], bitrate, len(refresh_rate), refresh_rate)
                        # print(f'data \n {data}')
                        all_data[sheet_name] = data
                        # print(f'all_data \n {all_data}')
                        # print(get_jod_score(all_data, 'path3_seg3_2', 500, 30, '360'))
        
        print(f'all_data \n {all_data}')
