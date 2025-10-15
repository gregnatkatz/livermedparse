#!/usr/bin/env python3
"""Generate mock hip CT images with red bone overlays for demo"""

import numpy as np
from PIL import Image, ImageDraw
import base64
from io import BytesIO
import os

def create_hip_ct_with_overlay():
    """Create realistic-looking hip CT scan with red bone segmentation overlay"""
    
    views = [
        "axial",
        "coronal", 
        "sagittal",
        "3d_anterior",
        "3d_lateral",
        "3d_superior"
    ]
    
    output_dir = "/home/ubuntu/livermedparse/backend/data/hip_ct_scans"
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, view in enumerate(views):
        img = np.random.randint(20, 60, (600, 800), dtype=np.uint8)
        
        for _ in range(50):
            x, y = np.random.randint(0, 800), np.random.randint(0, 600)
            size = np.random.randint(30, 100)
            img[max(0,y-size):min(600,y+size), max(0,x-size):min(800,x+size)] = np.random.randint(10, 30)
        
        rgb_image = np.stack([img] * 3, axis=-1)
        
        pil_img = Image.fromarray(rgb_image)
        draw = ImageDraw.Draw(pil_img, 'RGBA')
        
        if view in ["axial", "coronal", "sagittal"]:
            femur_coords = [
                (250, 400), (300, 380), (350, 390), 
                (380, 420), (370, 480), (340, 520),
                (300, 540), (260, 520), (240, 470)
            ]
            draw.polygon(femur_coords, fill=(255, 60, 60, 120), outline=(255, 0, 0, 200))
            
            pelvis_coords = [
                (450, 250), (550, 240), (620, 280),
                (650, 350), (620, 400), (550, 420),
                (480, 400), (450, 350)
            ]
            draw.polygon(pelvis_coords, fill=(255, 60, 60, 120), outline=(255, 0, 0, 200))
            
            draw.ellipse([480, 340, 560, 420], fill=(255, 80, 80, 140), outline=(255, 20, 20, 220))
            
        else:  # 3D views
            draw.ellipse([350, 200, 450, 300], fill=(255, 70, 70, 130), outline=(255, 10, 10, 210))
            
            neck_coords = [(380, 280), (420, 280), (430, 350), (370, 350)]
            draw.polygon(neck_coords, fill=(255, 60, 60, 120), outline=(255, 0, 0, 200))
            
            pelvis_3d = [
                (300, 150), (500, 150), (550, 200),
                (560, 280), (520, 320), (480, 330),
                (400, 330), (360, 320), (320, 280),
                (310, 200)
            ]
            draw.polygon(pelvis_3d, fill=(255, 60, 60, 120), outline=(255, 0, 0, 200))
        
        bone_pixels = np.random.randint(0, 800, (100, 2))
        for bx, by in bone_pixels:
            if by < 600:
                pil_img.putpixel((bx, by), (240, 100, 100))
        
        output_path = f"{output_dir}/hip_ct_{view}.png"
        pil_img.save(output_path, "PNG")
        print(f"Created: {output_path}")
        
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        with open(f"{output_path}.b64", "w") as f:
            f.write(f"data:image/png;base64,{img_str}")

if __name__ == "__main__":
    create_hip_ct_with_overlay()
    print("\n✅ Generated 6 hip CT images with red bone segmentation overlays")
