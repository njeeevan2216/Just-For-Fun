import os
import shutil
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_file_metadata(file_path):
    """
    Get the file's creation and modification times.
    
    :param file_path: Path to the file.
    :return: A tuple containing the creation and modification times.
    """
    creation_time = os.path.getctime(file_path)  # Creation time
    modification_time = os.path.getmtime(file_path)  # Last modification time
    return creation_time, modification_time

def apply_file_metadata(file_path, creation_time, modification_time):
    """
    Apply the creation and modification times to the specified file.
    
    :param file_path: Path to the file.
    :param creation_time: Creation time to apply.
    :param modification_time: Modification time to apply.
    """
    os.utime(file_path, (modification_time, creation_time))

def load_image(file_path):
    """Loads an image and converts it to a PyTorch tensor."""
    img = Image.open(file_path).convert("RGB")
    img_tensor = transforms.ToTensor()(img)  # Convert to tensor
    return img_tensor

def save_image(tensor, output_path):
    """Saves a PyTorch tensor as an image."""
    img_pil = transforms.ToPILImage()(tensor)
    img_pil.save(output_path, "JPEG", quality=85, optimize=True)

def resize_batch(batch, target_resolution):
    """
    Resizes a batch of images while preserving the aspect ratio.
    """
    resized_batch = []
    
    for img_tensor in batch:
        _, original_height, original_width = img_tensor.shape
        
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
            img_tensor = F.interpolate(img_tensor.unsqueeze(0), size=(new_height, new_width), mode='bilinear', align_corners=False).squeeze(0)
        
        resized_batch.append(img_tensor)

    return resized_batch

def process_batch(batch, file_paths, output_dir, target_resolution):
    """
    Processes a batch of image files by resizing and compressing them using PyTorch,
    while preserving the file metadata.
    """
    try:
        # Move batch to GPU
        batch = [img.to(device) for img in batch]

        # Resize the batch
        resized_batch = resize_batch(batch, target_resolution)

        # Save each image in the batch
        for img_tensor, file_path in zip(resized_batch, file_paths):
            output_path = os.path.join(output_dir, os.path.basename(file_path))
            
            # Save the compressed image
            save_image(img_tensor.cpu(), output_path)  # Move back to CPU for saving
            
            # Get and apply file metadata (creation and modification times)
            creation_time, modification_time = get_file_metadata(file_path)
            apply_file_metadata(output_path, creation_time, modification_time)
            
            print(f"Compressed: {file_path} -> {output_path} (metadata retained)")
    except Exception as e:
        print(f"Error processing batch {file_paths}: {e}")

def process_file(file_path, output_dir, target_resolution):
    """
    Processes an individual file: compresses it if it's an image, otherwise just copies it.
    """
    file = os.path.basename(file_path)
    output_path = os.path.join(output_dir, file)

    if file.lower().endswith(('.jpg', '.jpeg')):
        return load_image(file_path)  # Return the loaded image as a tensor
    else:
        try:
            # If not a JPEG image, copy the file without modification
            shutil.copy2(file_path, output_path)
            # Copy the metadata (creation/modification dates)
            creation_time, modification_time = get_file_metadata(file_path)
            apply_file_metadata(output_path, creation_time, modification_time)
            print(f"Copied: {file_path} -> {output_path} (metadata retained)")
        except Exception as e:
            print(f"Error copying file {file_path}: {e}")
        return None  # Non-image files are handled immediately

def compress_images(root_folder, output_folder, target_resolution=(800, 600), max_workers=4, batch_size=8):
    """
    Crawls through the given folder and compresses JPEG images in batches, preserving the aspect ratio and saving them
    in a different output folder while preserving the directory structure and metadata. Non-image files are copied without modification.
    
    Uses multithreading to parallelize the I/O and batching process.
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

    # Batch processing
    batch = []
    batch_file_paths = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for file_task in file_tasks:
            file_path, output_dir, target_resolution = file_task

            # Process the file (load the image or copy the file)
            img_tensor = process_file(file_path, output_dir, target_resolution)

            if img_tensor is not None:  # If it’s a valid image
                batch.append(img_tensor)
                batch_file_paths.append(file_path)

            # If batch is full, submit it for processing
            if len(batch) >= batch_size:
                futures.append(executor.submit(process_batch, batch, batch_file_paths, output_dir, target_resolution))
                batch = []  # Reset the batch
                batch_file_paths = []

        # Process remaining images in the last batch
        if batch:
            futures.append(executor.submit(process_batch, batch, batch_file_paths, output_dir, target_resolution))

        # Wait for all batches to finish
        for future in futures:
            future.result()

    print("====================")
    print("========DONE========")
    print("====================")

# Example usage
root_folder = r"D:\Year 2022-2023 Odd Sem Pics Comp"  # Change this to your target directory
output_folder = r"D:\Year 2022-2023 Odd Sem Pics Comp1"  # Change this to your output directory
target_resolution = (3000, 3000)  # Change this to your desired maximum resolution
compress_images(root_folder, output_folder, target_resolution, max_workers=8, batch_size=16)  # Adjust max_workers and batch_size
