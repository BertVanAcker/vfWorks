import os
import shutil
import yaml

# File to copy
original_file = "dataset\labels\img_0000.txt"
output_folder="dataset\labels"
train_folder = os.path.join(output_folder, "train")
validation_folder = os.path.join(output_folder, "val")

# Check if original file exists
if not os.path.exists(original_file):
    print(f"Error: {original_file} not found!")
    exit(1)

os.makedirs(output_folder, exist_ok=True)
os.makedirs(train_folder, exist_ok=True)
os.makedirs(validation_folder, exist_ok=True)

img_total = 100

# Copy 100 times with incremental names
for i in range(1, img_total):
    # Format the number with leading zeros (0001, 0002, etc.)
    new_number = f"{i:04d}"
    if i >= 0.67 * img_total:
        new_filename = os.path.join(validation_folder, f"img_{new_number}.txt")
    else:
        new_filename = os.path.join(train_folder, f"img_{new_number}.txt")

    # Copy the file
    shutil.copy2(original_file, new_filename)
    print(f"Created: {new_filename}")

annotation = dict(names = {1:"noscrew", 0:"screw"}, dataset_size=img_total, screws_samples=img_total*2, noscrews_samples=img_total*16)
with open("dataset/annotations_metadata.yaml", "w") as f:
    yaml.dump(annotation, f)
print(f"\nSuccessfully created 100 copies of {original_file}")