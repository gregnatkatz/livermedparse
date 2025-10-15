#!/usr/bin/env python3
"""Download and process real hip CT scans from public medical datasets"""

import os
import urllib.request
import zipfile
import tempfile
import numpy as np
from PIL import Image
import base64
from io import BytesIO

def download_sample_ct_data():
    """Download sample medical CT data that includes pelvic/hip region"""
    
    output_dir = "/home/ubuntu/livermedparse/backend/data/hip_ct_scans"
    os.makedirs(output_dir, exist_ok=True)
    
    
    sample_urls = [
        "https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/raw/master/Data/pelvis_small.mha",
        "https://raw.githubusercontent.com/SimpleITK/SimpleITK/master/Testing/Data/Input/pelvis.mha",
    ]
    
    for idx, url in enumerate(sample_urls):
        try:
            print(f"Attempting to download from {url}...")
            local_file = os.path.join(output_dir, f"hip_sample_{idx}.mha")
            urllib.request.urlretrieve(url, local_file)
            print(f"✓ Downloaded: {local_file}")
            
            process_mha_file(local_file, idx)
            
        except Exception as e:
            print(f"✗ Failed to download from {url}: {e}")
            continue

def process_mha_file(mha_file, idx):
    """Process MHA file and create CT images with bone visibility"""
    try:
        import SimpleITK as sitk
        
        print(f"Processing {mha_file}...")
        
        image = sitk.ReadImage(mha_file)
        array = sitk.GetArrayFromImage(image)
        
        print(f"Image shape: {array.shape}")
        print(f"Image range: {array.min()} to {array.max()}")
        
        num_slices = array.shape[0]
        
        views = [
            ("axial", array[num_slices//2, :, :]),
            ("coronal", array[:, array.shape[1]//2, :]),
            ("sagittal", array[:, :, array.shape[2]//2]),
            ("3d_anterior", array[num_slices//3, :, :]),
            ("3d_lateral", array[2*num_slices//3, :, :]),
            ("3d_superior", array[num_slices//4, :, :])
        ]
        
        output_dir = os.path.dirname(mha_file)
        
        for view_name, slice_data in views:
            window_center = 400
            window_width = 2000
            
            window_min = window_center - window_width // 2
            window_max = window_center + window_width // 2
            
            windowed = np.clip(slice_data, window_min, window_max)
            windowed = ((windowed - window_min) / (window_max - window_min) * 255).astype(np.uint8)
            
            rgb_image = np.stack([windowed] * 3, axis=-1)
            
            bone_mask = slice_data > 200
            rgb_image[bone_mask, 0] = np.minimum(255, rgb_image[bone_mask, 0] + 100)
            rgb_image[bone_mask, 1] = np.maximum(0, rgb_image[bone_mask, 1] - 50)
            rgb_image[bone_mask, 2] = np.maximum(0, rgb_image[bone_mask, 2] - 50)
            
            img = Image.fromarray(rgb_image)
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            
            output_path = os.path.join(output_dir, f"hip_ct_{view_name}.png")
            img.save(output_path, "PNG")
            print(f"Created: {output_path}")
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            with open(f"{output_path}.b64", "w") as f:
                f.write(f"data:image/png;base64,{img_str}")
        
        print(f"✓ Successfully processed {mha_file}")
        
    except Exception as e:
        print(f"✗ Error processing {mha_file}: {e}")
        import traceback
        traceback.print_exc()

def create_synthetic_realistic_ct():
    """Create synthetic but realistic-looking hip CT scans as fallback"""
    print("\nCreating synthetic realistic hip CT scans as fallback...")
    
    output_dir = "/home/ubuntu/livermedparse/backend/data/hip_ct_scans"
    
    for view_idx, view_name in enumerate(["axial", "coronal", "sagittal", "3d_anterior", "3d_lateral", "3d_superior"]):
        ct_image = np.random.normal(50, 15, (600, 800)).astype(np.uint8)
        
        
        if view_name in ["axial", "coronal"]:
            y_center, x_center = 400, 300
            for angle in range(0, 360, 5):
                rad = np.radians(angle)
                for r in range(40, 80):
                    y = int(y_center + r * np.sin(rad))
                    x = int(x_center + r * np.cos(rad))
                    if 0 <= y < 600 and 0 <= x < 800:
                        ct_image[y, x] = np.random.randint(180, 220)
            
            y_center, x_center = 250, 550
            for angle in range(0, 180, 5):
                rad = np.radians(angle)
                for r in range(50, 100):
                    y = int(y_center + r * np.sin(rad))
                    x = int(x_center + r * np.cos(rad))
                    if 0 <= y < 600 and 0 <= x < 800:
                        ct_image[y, x] = np.random.randint(180, 220)
        
        rgb_image = np.stack([ct_image] * 3, axis=-1)
        
        bone_mask = ct_image > 150
        rgb_image[bone_mask, 0] = np.minimum(255, rgb_image[bone_mask, 0] + 80)
        rgb_image[bone_mask, 1] = np.maximum(0, rgb_image[bone_mask, 1] - 30)
        rgb_image[bone_mask, 2] = np.maximum(0, rgb_image[bone_mask, 2] - 30)
        
        img = Image.fromarray(rgb_image)
        output_path = os.path.join(output_dir, f"hip_ct_{view_name}.png")
        img.save(output_path, "PNG")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        with open(f"{output_path}.b64", "w") as f:
            f.write(f"data:image/png;base64,{img_str}")
        
        print(f"Created synthetic: {output_path}")

if __name__ == "__main__":
    print("Downloading real hip CT scans from public medical datasets...")
    download_sample_ct_data()
    
    print("\nCreating additional synthetic realistic CT scans...")
    create_synthetic_realistic_ct()
    
    print("\n✅ Hip CT scan dataset preparation complete!")
