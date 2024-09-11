import os
import shutil
from PIL import Image
import csv

def compress_images(root_folder, output_folder, target_resolution=(800, 600)):
    """
    Crawls through the given folder and compresses all JPEG images to the specified resolution,
    saving them in a different output folder while preserving the directory structure.
    
    :param root_folder: The root directory to start searching for images.
    :param output_folder: The directory where compressed images will be saved.
    :param target_resolution: A tuple specifying the desired width and height.
    """
    f= open("log.csv", 'a+')
    pen= csv.writer(f, delimiter=',')
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(subdir, file)
            # Create the corresponding output directory structure
            relative_path = os.path.relpath(subdir, root_folder)
            output_dir = os.path.join(output_folder, relative_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the compressed image in the output folder
            output_path = os.path.join(output_dir, file)
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                try:
                    with Image.open(file_path) as img:
                        # Get original dimensions
                        original_width, original_height = img.size
                        
                        # Calculate aspect ratio and new dimensions
                        target_width, target_height = target_resolution
                        aspect_ratio = original_width / original_height
                        
                        if original_width > target_width or original_height > target_height:
                            # Resize based on the longer side
                            if aspect_ratio > 1:  # Wider than tall
                                new_width = target_width
                                new_height = int(target_width / aspect_ratio)
                            else:  # Taller than wide
                                new_height = target_height
                                new_width = int(target_height * aspect_ratio)
                            
                            img = img.resize((new_width, new_height), Image.LANCZOS)
                        
                        img.save(output_path, optimize=True, quality=85)
                        pen.writerow(("Compressed:", file_path, "->", output_path))
                        print(f"Compressed: {file_path} -> {output_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
            else:
                try:
                    # If not a JPEG image, copy the file without modification
                    shutil.copy2(file_path, output_path)
                    print(f"Copied: {file_path} -> {output_path}")
                except Exception as e:
                    print(f"Error copying file {file_path}: {e}")
        
    f.close()
    print("====================")
    print("========DONE========")
    print("====================")

root_folder = r"D:\Year 2022-2023 Odd Sem Pics"  # Change this to your target directory
output_folder = r"D:\Year 2022-2023 Odd Sem Pics Comp"  # Change this to your output directory
target_resolution = (3000, 3000)  # Change this to your desired resolution
compress_images(root_folder, output_folder, target_resolution)


#version 22
import os
import shutil
from PIL import Image
import concurrent.futures

def process_file(file_path, output_dir, target_resolution):
    """
    Processes an individual file: compresses it if it's an image, otherwise just copies it.
    """
    file = os.path.basename(file_path)
    output_path = os.path.join(output_dir, file)

    if file.lower().endswith(('.jpg', '.jpeg')):
        try:
            with Image.open(file_path) as img:
                # Get original dimensions
                original_width, original_height = img.size
                
                # Calculate aspect ratio and new dimensions
                target_width, target_height = target_resolution
                aspect_ratio = original_width / original_height
                
                if original_width > target_width or original_height > target_height:
                    # Resize based on the longer side
                    if aspect_ratio > 1:  # Wider than tall
                        new_width = target_width
                        new_height = int(target_width / aspect_ratio)
                    else:  # Taller than wide
                        new_height = target_height
                        new_width = int(target_height * aspect_ratio)
                    
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Save the compressed image in the output folder
                img.save(output_path, optimize=True, quality=85)
                
                print(f"Compressed: {file_path} -> {output_path}")
        except Exception as e:
            print(f"Error processing image {file_path}: {e}")
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
    the directory structure. Non-image files are copied without modification. The process is parallelized.
    
    :param root_folder: The root directory to start searching for images.
    :param output_folder: The directory where compressed images and copied files will be saved.
    :param target_resolution: A tuple specifying the maximum width and height while preserving aspect ratio.
    :param max_workers: Number of threads to use for processing files in parallel.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for subdir, _, files in os.walk(root_folder):
            relative_path = os.path.relpath(subdir, root_folder)
            output_dir = os.path.join(output_folder, relative_path)
            os.makedirs(output_dir, exist_ok=True)
            
            for file in files:
                file_path = os.path.join(subdir, file)
                # Submit the task for parallel execution
                futures.append(executor.submit(process_file, file_path, output_dir, target_resolution))

        # Wait for all threads to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Will raise any exceptions that occurred during processing
            except Exception as e:
                print(f"Error during parallel processing: {e}")

    print("====================")
    print("========DONE========")
    print("====================")

# Example usage
root_folder = r"D:\Year 2013-2014 Odd Sem"  # Change this to your target directory
output_folder = r"D:\Year 2013-2014 Odd Sem Comp"  # Change this to your output directory
target_resolution = (3000, 3000)  # Change this to your desired maximum resolution
compress_images(root_folder, output_folder, target_resolution, max_workers=8)  # Adjust max_workers for parallelism

#version33

import os
import shutil
from PIL import Image
import concurrent.futures

def process_file(file_path, output_dir, target_resolution):
    """
    Processes an individual file: compresses it if it's an image, otherwise just copies it.
    """
    file = os.path.basename(file_path)
    output_path = os.path.join(output_dir, file)

    if file.lower().endswith(('.jpg', '.jpeg')):
        try:
            with Image.open(file_path) as img:
                # Get original dimensions
                original_width, original_height = img.size
                
                # Calculate aspect ratio and new dimensions
                target_width, target_height = target_resolution
                aspect_ratio = original_width / original_height
                
                if original_width > target_width or original_height > target_height:
                    # Resize based on the longer side
                    if aspect_ratio > 1:  # Wider than tall
                        new_width = target_width
                        new_height = int(target_width / aspect_ratio)
                    else:  # Taller than wide
                        new_height = target_height
                        new_width = int(target_height * aspect_ratio)
                    
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Save the compressed image in the output folder
                img.save(output_path, optimize=True, quality=85)
                
                print(f"Compressed: {file_path} -> {output_path}")
        except Exception as e:
            print(f"Error processing image {file_path}: {e}")
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
    the directory structure. Non-image files are copied without modification. The process is parallelized.
    
    :param root_folder: The root directory to start searching for images.
    :param output_folder: The directory where compressed images and copied files will be saved.
    :param target_resolution: A tuple specifying the maximum width and height while preserving aspect ratio.
    :param max_workers: Number of threads to use for processing files in parallel.
    """
    # A list to hold file paths for processing
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # A list to keep track of all futures
        futures = {executor.submit(process_file, task[0], task[1], task[2]): task for task in file_tasks}
        
        # Process as each thread completes
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
root_folder = r"D:\Year 2013-2014 Odd Sem"  # Change this to your target directory
output_folder = r"D:\Year 2013-2014 Odd Sem Comp"  # Change this to your output directory
target_resolution = (3000, 3000)  # Change this to your desired maximum resolution
compress_images(root_folder, output_folder, target_resolution, max_workers=8)  # Adjust max_workers for parallelism
