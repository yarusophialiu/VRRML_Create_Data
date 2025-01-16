import numpy as np
import math


def read_dat_file(filename):
    with open(filename, 'rb') as file:
        data = file.read()
        return data


def compute_velocity(data, frame_rate):
    velocities = []
    for i in range(0, len(data) - 1, 2):
        t1 = data[i]
        t2 = data[i + 1]
        hypotenuse = math.sqrt(t1 * t1 + t2 * t2)
        velocity = frame_rate * hypotenuse
        print(f't1, t2, velocity {t1, t2, velocity}')

        velocities.append(velocity)
    return velocities



# Example usage
scene = 'bistro'
refresh_rate = 30
resolution = 360
path = 1
seg = 2
speed = 1
# TODO: change path of dat files
base_path = f'C:/Users/15142/new/Falcor/Source/Samples/EncodeDecode/motion/{scene}_path{path}_seg{seg}_{speed}/8000kbps/fps{refresh_rate}/{refresh_rate}_{resolution}_8000'
# base_path = r'C:\Users\15142\new\Falcor\Source\Samples\EncodeDecode\motion\suntemple_path4_seg1_1\8000kbps\fps{refresh_rate}\{refresh_rate}_{resolution}_8000'
# show motion vector of first 4 frames
# 4147200 = 1920 x 1080 x 2, each pixel has 2 floats
# 460800 = 640 x 360 x 2
# data logged from falcor: count fCount 79, t1 0.0507232, t2 0.0462358
for i in range(78, 81):
    filename = f'{base_path}/{i}_{refresh_rate}_{resolution}_8000_1.dat'
    data = read_dat_file(filename)

    data_array = np.frombuffer(data, dtype=np.float32)
    print(f'Frame {i}, shape {data_array.shape}')
    print(data_array[:10])


# Frame 78, shape (460800,)
# [0.0486628  0.04438757 0.04853966 0.0443831  0.04841661 0.04437872
#  0.04829351 0.04437428 0.04817046 0.04436987]
# Frame 79, shape (460800,)
# [0.05072315 0.04623576 0.05060514 0.04624047 0.05048713 0.04624515
#  0.05036906 0.04624989 0.05025099 0.04625459]
# Frame 80, shape (460800,)
# [0.05025842 0.04578193 0.05014154 0.04578652 0.05002472 0.04579126
#  0.04990781 0.04579588 0.0497909  0.04580062]