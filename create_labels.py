import os


JODs4000 = {
    # 4000 1080 864 720 480 360
    60: [7.4184, 7.3124, 7.1115, 6.9, 6.7021,],
    70: [7.6549, 7.5675, 7.4122, 7.2358, 7.0402,],
    80: [7.8837, 7.7779, 7.6665, 7.4091, 7.1709,],
    90: [7.8403, 7.7722, 7.7039, 7.5186, 7.2843,],
    10: [7.8066, 7.8162, 7.7529, 7.5565, 7.3289,],
    11: [7.7734, 7.7273, 7.7162, 7.5713, 7.3707,],
    12: [7.7309, 7.8129, 7.7026, 7.5979, 7.3579,],
}

JOD8000s = {60: [7.596, 7.4356, 7.2372, 7.0347, 6.8394,],
            70: [7.9234, 7.817, 7.623, 7.4477, 7.2221,],
            80: [8.2735, 8.1333, 7.8972, 7.6778, 7.3922,],
            90: [8.2045, 8.0959, 7.9976, 7.8333, 7.5588,],
            100: [8.2471, 8.1898, 8.1053, 7.9108, 7.6091,],
            110: [8.2707, 8.1953, 8.1378, 7.9737, 7.6955,],
            120: [8.3032, 8.2869, 8.2404, 7.9828, 7.7041,],}

JOD16000s = {60: [7.6625, 7.4908, 7.3033, 7.1097, 6.8946],
            70: [7.9977, 7.8477, 7.6857, 7.5487, 7.3069],
            80: [8.4064, 8.2019, 8.0356, 7.826, 7.5003],
            90: [8.3785, 8.2581, 8.1676, 8.0099, 7.6935],
            100: [8.4336, 8.3571, 8.2841, 8.1011, 7.7656],
            110: [8.4963, 8.4375, 8.3957, 8.2071, 7.8642],
            120: [8.5779, 8.5041, 8.4824, 8.2624, 7.9056],
            }

# Path to the base folder "8bps"
base_path = 'C:/Users/15142/Desktop/VRR/VRR_Patches/suntemple_tonemap/patch/16bps'

# Old folder names, assuming they are named fps60, fps70, fps80, fps90, fps100, fps110, fps120
old_names = [i for i in range(60, 121, 10)]
print(f'oldnames {old_names}')
resolutions = [1080, 864, 720, 480, 360]

# New folder names provided in the task
# new_names = ["7.596", "7.4356", "7.2372", "7.0347", "6.8394", "7.4392", "7.1279"]
bitrate = 16000
# Loop through old_names and rename them to new_names
for fps in old_names:
    fps_path =  os.path.join(base_path, f'fps{fps}')
    print(f'\n\n\nfps_path {fps_path}')
    for old_name, new_name in zip(resolutions, JOD16000s[fps]):
        old_path = os.path.join(fps_path, f'{fps}_{old_name}_{bitrate}')
        new_path = os.path.join(fps_path, str(new_name))
        os.rename(old_path, new_path)
        print(f'Renamed "{old_name}" to "{new_name}"')
