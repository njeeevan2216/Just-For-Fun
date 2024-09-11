import os
import shutil
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_image(file_path):
    """Loads an image and converts it to a PyTorch tensor."""
    img = Image.open(file_path).convert("RGB")
    img_tensor = transforms.ToTensor()(img).unsqueeze(0)  # Add batch dimension
    return img_tensor

def save_image(tensor, output_path):
    """Saves a PyTorch tensor as an image."""
    img = tensor.squeeze(0)  # Remove batch dimension
    img_pil = transforms.ToPILImage()(img)
    img_pil.save(output_path, "JPEG", quality=85, optimize=True)

def process_image(file_path, output_dir, target_resolution):
    """
    Processes an individual image file by resizing and compressing it using PyTorch.
    """
    try:
        # Load image as a tensor
        img_tensor = load_image(file_path).to(device)

        # Get original dimensions
        _, _, original_height, original_width = img_tensor.shape
        
        # Calculate new dimensions while preserving aspect ratio
        target_width, target_height = target_resolution
        aspect_ratio = original_width / original_height

        if original_width > target_width or original_height > target_height:
            if aspect_ratio > 1:  # Wider than tall
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:  # Taller than wide
                new_height = target_height
                new_width = int(target_height * aspect_ratio)

            # Resize using PyTorch (GPU accelerated)
            img_tensor = F.interpolate(img_tensor, size=(new_height, new_width), mode='bilinear', align_corners=False)

        # Save the compressed image
        output_path = os.path.join(output_dir, os.path.basename(file_path))
        save_image(img_tensor.cpu(), output_path)  # Move tensor back to CPU for saving

        print(f"Compressed: {file_path} -> {output_path}")
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")

def process_file(file_path, output_dir, target_resolution):
    """
    Processes an individual file: compresses it if it's an image, otherwise just copies it.
    """
    file = os.path.basename(file_path)
    output_path = os.path.join(output_dir, file)

    if file.lower().endswith(('.jpg', '.jpeg')):
        process_image(file_path, output_dir, target_resolution)
    else:
        try:
            # If not a JPEG image, copy the file without modification
            shutil.copy2(file_path, output_path)
            print(f"Copied: {file_path} -> {output_path}")
        except Exception as e:
            print(f"Error copying file {file_path}: {e}")

def compress_images(root_folder, output_folder, target_resolution=(800, 600), max_workers=4):
    """
    Crawls through the given folder and compresses all JPEG images to the specified resolution,
    preserving the aspect ratio and saving them in a different output folder while preserving
    the directory structure. Non-image files are copied without modification.
    
    Uses multithreading to parallelize the process.
    """
    file_tasks = []

    # Crawl through directories and collect tasks
    for subdir, _, files in os.walk(root_folder):
        relative_path = os.path.relpath(subdir, root_folder)
        output_dir = os.path.join(output_folder, relative_path)
        os.makedirs(output_dir, exist_ok=True)
        
        for file in files:
            file_path = os.path.join(subdir, file)
            file_tasks.append((file_path, output_dir, target_resolution))

    # Use ThreadPoolExecutor to handle multithreading
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, task[0], task[1], task[2]): task for task in file_tasks}
        
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            try:
                future.result()  # Check for exceptions
            except Exception as e:
                print(f"Error during processing file {task[0]}: {e}")

    print("====================")
    print("========DONE========")
    print("====================")

# Example usage
root_folder = r"D:\Year 2022-2023 Odd Sem Pics Comp"  # Change this to your target directory
output_folder = r"D:\Year 2022-2023 Odd Sem Pics Comp1"  # Change this to your output directory
target_resolution = (3000, 3000)  # Change this to your desired maximum resolution
compress_images(root_folder, output_folder, target_resolution, max_workers=32)  # Adjust max_workers for parallelism
