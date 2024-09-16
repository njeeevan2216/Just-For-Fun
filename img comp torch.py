import os
import shutil
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

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

def get_file_metadata(file_path):
    """
    Get the file's creation and modification times.
    :param file_path: Path to the file.
    :return: A tuple containing the creation and modification times.
    """
    creation_time = os.path.getctime(file_path)  # Creation time
    modification_time = os.path.getmtime(file_path)  # Last modification time
    return creation_time, modification_time

def apply_file_metadata(output_path, creation_time, modification_time):
    """
    Apply the creation and modification times to the specified file.
    :param output_path: Path to the file.
    :param creation_time: Creation time to apply.
    :param modification_time: Modification time to apply.
    """
    os.utime(output_path, (modification_time, creation_time))

def process_image(file_path, output_dir, target_resolution):
    """
    Processes an individual image file by resizing and compressing it using PyTorch,
    and applies the original file's metadata to the new image.
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

        # Get and apply file metadata (creation and modification times)
        creation_time, modification_time = get_file_metadata(file_path)
        apply_file_metadata(output_path, modification_time, modification_time)

        return True
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return False

def process_file(file_path, output_dir, target_resolution):
    """
    Processes an individual file: compresses it if it's an image, otherwise just copies it.
    Preserves file metadata.
    """
    file = os.path.basename(file_path)
    output_path = os.path.join(output_dir, file)

    if file.lower().endswith(('.jpg', '.jpeg')):
        return process_image(file_path, output_dir, target_resolution)
    else:
        try:
            # If not a JPEG image, copy the file without modification
            shutil.copy2(file_path, output_path)

            # Get and apply file metadata (creation and modification times)
            creation_time, modification_time = get_file_metadata(file_path)
            apply_file_metadata(output_path, modification_time, modification_time)

            return True
        except Exception as e:
            print(f"Error copying file {file_path}: {e}")
            return False

def compress_images(root_folder, output_folder, target_resolution=(800, 600), max_workers=4):
    """
    Crawls through the given folder and compresses all JPEG images to the specified resolution,
    preserving the aspect ratio and saving them in a different output folder while preserving
    the directory structure. Non-image files are copied without modification.
    
    Uses multithreading to parallelize the process and includes a progress bar.
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

    total_files = len(file_tasks)

    # Use ThreadPoolExecutor to handle multithreading with a progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, task[0], task[1], task[2]): task for task in file_tasks}
        
        with tqdm(total=total_files, desc="Processing files", unit="file") as pbar:
            for future in as_completed(futures):
                try:
                    future.result()  # Check for exceptions
                except Exception as e:
                    task = futures[future]
                    print(f"Error during processing file {task[0]}: {e}")
                pbar.update(1)  # Increment the progress bar after each file is processed

    print("====================")
    print("========DONE========")
    print("====================")

# Example usage
root_folder = r"D:\ODD SEM 2K23 for D2H"  # Change this to your target directory
output_folder = r"D:\ODD SEM 2K23 for D2H 1"  # Change this to your output directory
target_resolution = (3000, 3000)  # Change this to your desired maximum resolution
compress_images(root_folder, output_folder, target_resolution, max_workers=16)  # Adjust max_workers for parallelism
