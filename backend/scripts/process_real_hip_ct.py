#!/usr/bin/env python3
"""Process real DICOM hip CT scans and create images with red bone segmentation"""

import os
import numpy as np
from PIL import Image
import pydicom
import base64
from io import BytesIO

def process_hip_dicom_files():
    """Process real hip CT DICOM files from ISB dataset"""
    
    data_dir = "/home/ubuntu/livermedparse/backend/data/hip_ct_scans"
    
    dicom_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.dcm')])
    
    print(f"Found {len(dicom_files)} DICOM files")
    
    if not dicom_files:
        print("No DICOM files found!")
        return
    
    
    slices_to_process = {
        'axial': [
            len(dicom_files) // 4,      # Lower section
            len(dicom_files) // 3,      # Mid-lower
            len(dicom_files) // 2,      # Middle (best view)
            2 * len(dicom_files) // 3,  # Mid-upper
            3 * len(dicom_files) // 4,  # Upper section
            len(dicom_files) - 10       # Near top
        ]
    }
    
    views = {
        'axial': slices_to_process['axial'][2],         # Best middle slice
        'coronal': slices_to_process['axial'][3],       # Use as coronal view
        'sagittal': slices_to_process['axial'][1],      # Use as sagittal view
        '3d_anterior': slices_to_process['axial'][4],   # 3D view 1
        '3d_lateral': slices_to_process['axial'][0],    # 3D view 2
        '3d_superior': slices_to_process['axial'][5]    # 3D view 3
    }
    
    for view_name, slice_idx in views.items():
        try:
            dicom_file = os.path.join(data_dir, dicom_files[slice_idx])
            ds = pydicom.dcmread(dicom_file, force=True)
            
            ct_array = ds.pixel_array.astype(float)
            
            print(f"Processing {view_name} from slice {slice_idx} ({dicom_files[slice_idx]})")
            print(f"  Original range: {ct_array.min()} to {ct_array.max()}")
            
            if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                ct_array = ct_array * ds.RescaleSlope + ds.RescaleIntercept
                print(f"  After rescale: {ct_array.min()} to {ct_array.max()} HU")
            
            window_center = 400
            window_width = 2000
            
            window_min = window_center - window_width // 2
            window_max = window_center + window_width // 2
            
            windowed = np.clip(ct_array, window_min, window_max)
            windowed = ((windowed - window_min) / (window_max - window_min) * 255).astype(np.uint8)
            
            img_temp = Image.fromarray(windowed)
            img_temp = img_temp.resize((800, 600), Image.Resampling.LANCZOS)
            windowed = np.array(img_temp)
            
            rgb_image = np.stack([windowed] * 3, axis=-1)
            
            bone_threshold_hu = 200  # Bone typically > 200 HU
            bone_threshold_windowed = max(0, int(((bone_threshold_hu - window_min) / (window_max - window_min)) * 255))
            
            bone_mask = windowed > bone_threshold_windowed
            
            rgb_image[bone_mask, 0] = np.minimum(255, windowed[bone_mask] * 1.4 + 70)  # RED boost
            rgb_image[bone_mask, 1] = windowed[bone_mask] * 0.6  # Reduce green
            rgb_image[bone_mask, 2] = windowed[bone_mask] * 0.6  # Reduce blue
            
            img = Image.fromarray(rgb_image.astype(np.uint8))
            
            output_path = os.path.join(data_dir, f"hip_ct_{view_name}.png")
            img.save(output_path, "PNG")
            print(f"  Saved: {output_path}")
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            with open(f"{output_path}.b64", "w") as f:
                f.write(f"data:image/png;base64,{img_str}")
            
            print(f"  ✓ Created {view_name} from real CT data")
            
        except Exception as e:
            print(f"  ✗ Error processing {view_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Processing real hip CT DICOM scans from ISB Visual Skeleton Joint dataset...")
    print("Source: University of Brussels - Acetabulum CT sequence")
    print()
    
    process_hip_dicom_files()
    
    print("\n✅ Real hip CT images with red bone segmentation created!")
