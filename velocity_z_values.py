import os
import numpy as np

def extract_velocity_from_filename(filename):
    # Assuming the velocity is the last part before the .png and needs to be divided by 1000
    velocity_str = filename.split('_')[-1].replace('.png', '')
    velocity = float(velocity_str) / 1000  # Divide by 1000 as per your data description
    return velocity

def extract_velocity_stats(root_folder):
    # count = 0
    # Traverse the folder structure
    for path_folder in os.listdir(root_folder):
        path_folder_path = os.path.join(root_folder, path_folder)

        if os.path.isdir(path_folder_path):
            for bitrate_folder in os.listdir(path_folder_path):
                bitrate_folder_path = os.path.join(path_folder_path, bitrate_folder)

                if os.path.isdir(bitrate_folder_path):
                    for patch_file in os.listdir(bitrate_folder_path):
                        # if count >= 2:
                        #     return
                        if patch_file.endswith('.png'):
                            velocity = extract_velocity_from_filename(patch_file)
                            if velocity == 51918288.0:
                                print(f'max velocity {path_folder}， {bitrate_folder}， {patch_file}')
                            # max_v = velocity if velocity > max_v else max_v
                            # print(f'velocity {velocity}')
                            # count += 1
                            velocities.append(velocity)


# Define the root folder containing the training data
train_folder = r'C:\Users\15142\Projects\VRR\Data\VRRML\ML\train'  # Update with your actual path
validation_folder = r'C:\Users\15142\Projects\VRR\Data\VRRML\ML\validation'  # Update with your actual path
velocities = []
max_v = -1

# Extract the velocity statistics
extract_velocity_stats(train_folder)
print(f'velocities length {len(velocities)}')

extract_velocity_stats(validation_folder)
print(f'velocities length {len(velocities)}\n')

# Compute mean and std
velocities = np.array(velocities)
print(f'velocities {velocities}, max {np.sort(velocities)[::-1]}, min {min(velocities)}')
mean_velocity = np.mean(velocities)
std_velocity = np.std(velocities)

# Output the results
print(f"Mean Velocity: {mean_velocity}")
print(f"Standard Deviation of Velocity: {std_velocity}")