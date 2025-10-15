#!/usr/bin/env python3
"""Create realistic-looking hip CT scans based on actual CT imaging characteristics"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import base64
from io import BytesIO
import os

def create_realistic_ct_scan(view_type, output_dir):
    """Create a realistic CT scan image with proper bone/soft tissue contrast"""
    
    
    width, height = 800, 600
    
    ct_array = np.random.normal(110, 8, (height, width))
    
    noise = np.random.normal(0, 3, (height, width))
    ct_array += noise
    
    if view_type == "axial":
        create_axial_pelvis_anatomy(ct_array)
    elif view_type == "coronal":
        create_coronal_hip_anatomy(ct_array)
    elif view_type == "sagittal":
        create_sagittal_hip_anatomy(ct_array)
    elif "3d" in view_type:
        create_3d_hip_anatomy(ct_array, view_type)
    
    ct_array = np.clip(ct_array, 0, 255).astype(np.uint8)
    
    rgb_image = np.stack([ct_array] * 3, axis=-1)
    
    bone_mask = ct_array > 180
    rgb_image[bone_mask, 0] = 255  # RED channel - maximum
    rgb_image[bone_mask, 1] = np.maximum(0, ct_array[bone_mask] - 100)   # GREEN - much less
    rgb_image[bone_mask, 2] = np.maximum(0, ct_array[bone_mask] - 100)   # BLUE - much less
    
    img = Image.fromarray(rgb_image)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    output_path = os.path.join(output_dir, f"hip_ct_{view_type}.png")
    img.save(output_path, "PNG")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    with open(f"{output_path}.b64", "w") as f:
        f.write(f"data:image/png;base64,{img_str}")
    
    print(f"Created realistic CT: {output_path}")

def create_axial_pelvis_anatomy(ct_array):
    """Create axial view anatomy - femoral heads and acetabulum"""
    height, width = ct_array.shape
    
    draw_filled_circle(ct_array, 300, 350, 55, 220)  # Dense bone
    draw_filled_circle(ct_array, 300, 350, 40, 115)  # Medullary cavity (fat/marrow)
    
    draw_filled_circle(ct_array, 500, 350, 55, 220)
    draw_filled_circle(ct_array, 500, 350, 40, 115)
    
    draw_filled_ellipse(ct_array, 250, 280, 80, 120, 210)  # Left ilium
    draw_filled_ellipse(ct_array, 550, 280, 80, 120, 210)  # Right ilium
    
    draw_arc_structure(ct_array, 300, 320, 60, 180, 360, 215)
    draw_arc_structure(ct_array, 500, 320, 60, 180, 360, 215)
    
    draw_filled_rect(ct_array, 380, 200, 40, 100, 205)

def create_coronal_hip_anatomy(ct_array):
    """Create coronal view - femur and pelvis from front"""
    height, width = ct_array.shape
    
    draw_filled_rect(ct_array, 280, 350, 50, 200, 210)
    draw_filled_rect(ct_array, 290, 360, 30, 180, 120)  # Medullary cavity
    
    draw_filled_rect(ct_array, 520, 350, 50, 200, 210)
    draw_filled_rect(ct_array, 530, 360, 30, 180, 120)
    
    draw_filled_rect(ct_array, 250, 280, 35, 70, 215)
    draw_filled_rect(ct_array, 550, 280, 35, 70, 215)
    
    draw_filled_circle(ct_array, 265, 250, 40, 220)
    draw_filled_circle(ct_array, 535, 250, 40, 220)
    
    draw_filled_ellipse(ct_array, 400, 200, 200, 60, 205)

def create_sagittal_hip_anatomy(ct_array):
    """Create sagittal view - side view of hip"""
    height, width = ct_array.shape
    
    draw_filled_rect(ct_array, 380, 350, 60, 220, 210)
    draw_filled_rect(ct_array, 390, 360, 40, 200, 120)  # Medullary cavity
    
    draw_angled_rect(ct_array, 360, 280, 80, 35, 30, 215)
    
    draw_filled_circle(ct_array, 320, 260, 45, 220)
    draw_filled_circle(ct_array, 320, 260, 30, 115)
    
    draw_arc_structure(ct_array, 315, 235, 55, 200, 340, 215)
    draw_filled_ellipse(ct_array, 350, 180, 100, 80, 205)

def create_3d_hip_anatomy(ct_array, view_type):
    """Create 3D reconstruction view"""
    height, width = ct_array.shape
    
    if "anterior" in view_type:
        create_coronal_hip_anatomy(ct_array)
    elif "lateral" in view_type:
        create_sagittal_hip_anatomy(ct_array)
    else:  # superior
        create_axial_pelvis_anatomy(ct_array)

def draw_filled_circle(array, x, y, radius, intensity):
    """Draw a filled circle on the CT array"""
    height, width = array.shape
    Y, X = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((X - x)**2 + (Y - y)**2)
    mask = dist_from_center <= radius
    array[mask] = intensity

def draw_filled_ellipse(array, x, y, width_rad, height_rad, intensity):
    """Draw a filled ellipse"""
    height, width = array.shape
    Y, X = np.ogrid[:height, :width]
    mask = ((X - x)**2 / width_rad**2 + (Y - y)**2 / height_rad**2) <= 1
    array[mask] = intensity

def draw_filled_rect(array, x, y, w, h, intensity):
    """Draw filled rectangle"""
    y1, y2 = max(0, y), min(array.shape[0], y + h)
    x1, x2 = max(0, x), min(array.shape[1], x + w)
    array[y1:y2, x1:x2] = intensity

def draw_arc_structure(array, cx, cy, radius, start_angle, end_angle, intensity):
    """Draw an arc (like acetabulum)"""
    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), 50)
    for angle in angles:
        for r in range(radius - 15, radius + 15):
            x = int(cx + r * np.cos(angle))
            y = int(cy + r * np.sin(angle))
            if 0 <= y < array.shape[0] and 0 <= x < array.shape[1]:
                array[y, x] = intensity

def draw_angled_rect(array, x, y, w, h, angle_deg, intensity):
    """Draw rotated rectangle (for femoral neck)"""
    angle = np.radians(angle_deg)
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    
    for dy in range(h):
        for dx in range(w):
            new_x = int(x + dx * cos_a - dy * sin_a)
            new_y = int(y + dx * sin_a + dy * cos_a)
            if 0 <= new_y < array.shape[0] and 0 <= new_x < array.shape[1]:
                array[new_y, new_x] = intensity

if __name__ == "__main__":
    output_dir = "/home/ubuntu/livermedparse/backend/data/hip_ct_scans"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating realistic hip CT scans with proper bone anatomy...")
    
    views = ["axial", "coronal", "sagittal", "3d_anterior", "3d_lateral", "3d_superior"]
    
    for view in views:
        create_realistic_ct_scan(view, output_dir)
    
    print("\n✅ Realistic hip CT scans created successfully!")
