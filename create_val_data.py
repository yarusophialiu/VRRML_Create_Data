import os
import random
import shutil

# Paths
train_root = r"D:\VRR_data\VRRML\ML\reference_dropJOD_64x64"  # Training data root
val_root = r"D:\VRR_data\VRRML\ML\validation-temp"   # Validation data root

# Ensure the validation directory exists
os.makedirs(val_root, exist_ok=True)
total_files = 0
total_validation_files = 0
# Iterate over each subfolder (e.g., "360x30", "480x60", etc.)
for subfolder in os.listdir(train_root):
    subfolder_path = os.path.join(train_root, subfolder)
    val_subfolder_path = os.path.join(val_root, subfolder)
    
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

print(f'total number of files {total_files}, train files {total_files - total_validation_files}, validation files {total_validation_files}')
print("Validation dataset created successfully!")
