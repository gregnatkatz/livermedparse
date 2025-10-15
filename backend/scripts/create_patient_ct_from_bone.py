#!/usr/bin/env python3
"""Create realistic patient CT scans by adding soft tissue to real bone specimens"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pydicom
from pydicom.uid import ImplicitVRLittleEndian
import base64
from io import BytesIO

def create_patient_ct_with_soft_tissue():
    """Take real bone CT and add realistic soft tissue"""
    
    data_dir = "/home/ubuntu/livermedparse/backend/data/hip_ct_scans"
    dicom_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.dcm')])
    
    print(f"Creating patient CT scans with soft tissue from {len(dicom_files)} DICOM files")
    
    views = {
        'axial': len(dicom_files) // 2,
        'coronal': len(dicom_files) // 3,
        'sagittal': 2 * len(dicom_files) // 3,
        '3d_anterior': len(dicom_files) // 4,
        '3d_lateral': 3 * len(dicom_files) // 4,
        '3d_superior': len(dicom_files) - 20
    }
    
    for view_name, slice_idx in views.items():
        try:
            dicom_file = os.path.join(data_dir, dicom_files[slice_idx])
            print(f"\nProcessing {view_name} from {dicom_files[slice_idx]}")
            
            ds = pydicom.dcmread(dicom_file, force=True)
            ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
            
            bone_array = ds.pixel_array.astype(float)
            if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                bone_array = bone_array * ds.RescaleSlope + ds.RescaleIntercept
            
            print(f"  Original bone CT: {bone_array.shape}, {bone_array.min():.1f} to {bone_array.max():.1f} HU")
            
            rows, cols = bone_array.shape
            patient_ct = np.ones((rows, cols), dtype=float) * -1000  # Start with air
            
            center_x, center_y = cols // 2, rows // 2
            
            for y in range(rows):
                for x in range(cols):
                    dx = (x - center_x) / (cols * 0.4)
                    dy = (y - center_y) / (rows * 0.45)
                    dist = dx**2 + dy**2
                    
                    if dist < 1:  # Inside body
                        patient_ct[y, x] = np.random.normal(45, 10)
                        
                        if dist > 0.8:
                            patient_ct[y, x] = np.random.normal(-60, 15)
            
            num_structures = 8
            for _ in range(num_structures):
                struct_x = np.random.randint(int(cols*0.3), int(cols*0.7))
                struct_y = np.random.randint(int(rows*0.3), int(rows*0.7))
                radius = np.random.randint(30, 80)
                intensity = np.random.choice([
                    np.random.normal(35, 5),   # Fat/organ
                    np.random.normal(55, 5),   # Muscle
                    np.random.normal(20, 5)    # Low density tissue
                ])
                
                for y in range(max(0, struct_y-radius), min(rows, struct_y+radius)):
                    for x in range(max(0, struct_x-radius), min(cols, struct_x+radius)):
                        if (x-struct_x)**2 + (y-struct_y)**2 <= radius**2:
                            patient_ct[y, x] = intensity
            
            bone_mask = bone_array > -500  # Where actual bone specimen is
            patient_ct[bone_mask] = bone_array[bone_mask]
            
            print(f"  Patient CT with soft tissue: {patient_ct.min():.1f} to {patient_ct.max():.1f} HU")
            
            window_center = 40
            window_width = 400
            window_min = window_center - window_width // 2
            window_max = window_center + window_width // 2
            
            windowed = np.clip(patient_ct, window_min, window_max)
            windowed = ((windowed - window_min) / (window_max - window_min) * 255).astype(np.uint8)
            
            img_temp = Image.fromarray(windowed)
            img_temp = img_temp.resize((800, 600), Image.Resampling.LANCZOS)
            windowed = np.array(img_temp)
            
            img_temp = Image.fromarray(windowed)
            img_temp = img_temp.filter(ImageFilter.GaussianBlur(radius=0.8))
            windowed = np.array(img_temp)
            
            rgb_image = np.stack([windowed] * 3, axis=-1)
            
            bone_threshold = 180
            bone_mask_display = windowed > bone_threshold
            
            rgb_image[bone_mask_display, 0] = np.minimum(255, windowed[bone_mask_display] * 1.2 + 60)
            rgb_image[bone_mask_display, 1] = windowed[bone_mask_display] * 0.7
            rgb_image[bone_mask_display, 2] = windowed[bone_mask_display] * 0.7
            
            img = Image.fromarray(rgb_image.astype(np.uint8))
            output_path = os.path.join(data_dir, f"hip_ct_{view_name}.png")
            img.save(output_path, "PNG")
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            with open(f"{output_path}.b64", "w") as f:
                f.write(f"data:image/png;base64,{img_str}")
            
            print(f"  ✓ Created patient CT with visible soft tissue and bones")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("Creating realistic PATIENT hip CT scans")
    print("Real bone anatomy + synthetic soft tissue")
    print("="*60)
    create_patient_ct_with_soft_tissue()
    print("\n✅ Patient CT scans with soft tissue created!")
