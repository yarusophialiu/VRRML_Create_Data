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



patch = torch.tensor([[[  0,   0,   0,   0,   0,   0,   0,   0],
         [  0,   0,   0,   0,   0,   0,   0,   0],
         [  0,   0,   0,   0,   0,   0,   0,   0],
         [  0,   0,   0,   0,   0,   0,   0,   0],
         [  0,   0,   0,   0,   0,   0,   0,   0],
         [  0,   0,   0,   0,   0,   0,   0,   0],
         [  0,   0,   0,   0,   0,   0,   0,   0],
         [  0,   0,   0,   0,   0,   0,   0,   0]],

        [[154, 154, 154, 154, 154, 154, 154, 154],
         [154, 154, 154, 154, 154, 154, 154, 154],
         [154, 154, 154, 154, 154, 154, 154, 154],
         [154, 154, 154, 154, 154, 154, 154, 154],
         [154, 154, 154, 154, 154, 154, 154, 154],
         [154, 154, 154, 154, 154, 154, 154, 154],
         [154, 154, 154, 154, 154, 154, 154, 154],
         [154, 154, 154, 154, 154, 154, 154, 154]],

        [[184, 184, 184, 184, 184, 184, 184, 184],
         [184, 184, 184, 184, 184, 184, 184, 184],
         [184, 184, 184, 184, 184, 184, 184, 184],
         [184, 184, 184, 184, 184, 184, 184, 184],
         [184, 184, 184, 184, 184, 184, 184, 184],
         [184, 184, 184, 184, 184, 184, 184, 184],
         [184, 184, 184, 184, 184, 184, 184, 184],
         [184, 184, 184, 184, 184, 184, 184, 184]]])

h, w = patch.shape[1], patch.shape[2]  # height and width
print(h, w)

blue_channel = patch[0, :, :]
odd_channel_processed = patch[1, :, :].float()  # Convert to float for calculations
even_channel_processed = patch[2, :, :].float()
# print(odd_channel_processed)

pixel_precision = 3
even_channel = (((even_channel_processed / 255.0) * 2) - 1) * pixel_precision
even_channel = even_channel / (0.5 * w)  # Undo the scaling based on width

# Undo the transformations for odd channel
odd_channel = (((odd_channel_processed / 255.0) * 2) - 1) * pixel_precision
odd_channel = odd_channel / (0.5 * h)  # Undo the scaling based on height

# print(f'even_channel \n {even_channel}')
# print(f'odd_channel \n {odd_channel}')
# print(even_channel**2)
# print(odd_channel**2)

squared_sum = odd_channel ** 2 + even_channel ** 2

# Compute the square root of the sum
# print(f'squared_sum \n {squared_sum}')

sqrt_result = torch.sqrt(squared_sum)

print("Square root of odd^2 + even^2:\n", sqrt_result)
total_sum = sqrt_result.sum()

# Take the average of sqrt_result
average = sqrt_result.mean()

print("Sum of sqrt_result:", total_sum.item())
print("Average of sqrt_result:", average.item())
