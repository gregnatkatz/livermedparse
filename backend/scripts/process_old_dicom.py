#!/usr/bin/env python3
"""Process old DICOM files that lack proper headers"""

import os
import numpy as np
from PIL import Image
import pydicom
from pydicom.uid import ImplicitVRLittleEndian
import base64
from io import BytesIO

def process_old_dicom():
    """Process old DICOM files with manual transfer syntax"""
    
    data_dir = "/home/ubuntu/livermedparse/backend/data/hip_ct_scans"
    
    dicom_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.dcm')])
    
    print(f"Found {len(dicom_files)} DICOM files")
    
    views = {
        'axial': len(dicom_files) // 2,          # Middle slice
        'coronal': len(dicom_files) // 3,        # Lower third
        'sagittal': 2 * len(dicom_files) // 3,   # Upper third
        '3d_anterior': len(dicom_files) // 4,    # Quarter
        '3d_lateral': 3 * len(dicom_files) // 4, # Three quarters
        '3d_superior': len(dicom_files) - 20     # Near top
    }
    
    for view_name, slice_idx in views.items():
        try:
            dicom_file = os.path.join(data_dir, dicom_files[slice_idx])
            print(f"Processing {view_name} from {dicom_files[slice_idx]}")
            
            ds = pydicom.dcmread(dicom_file, force=True)
            
            ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
            
            try:
                ct_array = ds.pixel_array.astype(float)
            except:
                print(f"  Trying raw pixel data access...")
                pixel_data = ds.PixelData
                rows = ds.Rows
                cols = ds.Columns
                bits = ds.BitsAllocated
                
                if bits == 16:
                    ct_array = np.frombuffer(pixel_data, dtype=np.uint16).reshape((rows, cols))
                elif bits == 8:
                    ct_array = np.frombuffer(pixel_data, dtype=np.uint8).reshape((rows, cols))
                else:
                    raise ValueError(f"Unsupported bits allocated: {bits}")
                
                ct_array = ct_array.astype(float)
            
            print(f"  Array shape: {ct_array.shape}, range: {ct_array.min()} to {ct_array.max()}")
            
            if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                ct_array = ct_array * ds.RescaleSlope + ds.RescaleIntercept
                print(f"  After rescale: {ct_array.min()} to {ct_array.max()} HU")
            
            window_center = 40
            window_width = 400
            window_min = window_center - window_width // 2
            window_max = window_center + window_width // 2
            
            windowed = np.clip(ct_array, window_min, window_max)
            windowed = ((windowed - window_min) / (window_max - window_min) * 255).astype(np.uint8)
            
            img_temp = Image.fromarray(windowed)
            img_temp = img_temp.resize((800, 600), Image.Resampling.LANCZOS)
            windowed = np.array(img_temp)
            
            rgb_image = np.stack([windowed] * 3, axis=-1)
            
            bone_mask = windowed > 180
            rgb_image[bone_mask, 0] = np.minimum(255, windowed[bone_mask] * 1.2 + 60)
            rgb_image[bone_mask, 1] = windowed[bone_mask] * 0.7
            rgb_image[bone_mask, 2] = windowed[bone_mask] * 0.7
            
            img = Image.fromarray(rgb_image.astype(np.uint8))
            output_path = os.path.join(data_dir, f"hip_ct_{view_name}.png")
            img.save(output_path, "PNG")
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            with open(f"{output_path}.b64", "w") as f:
                f.write(f"data:image/png;base64,{img_str}")
            
            print(f"  ✓ Created {view_name}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Processing old DICOM hip CT scans...")
    process_old_dicom()
    print("\n✅ Done!")
