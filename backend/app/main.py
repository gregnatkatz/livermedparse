from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import base64
from io import BytesIO

from app.config import settings
from app.services import get_ai_service

app = FastAPI(title="Medical Imaging AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "mode": "mock" if settings.USE_MOCK_DATA else "production",
        "version": "1.0.0"
    }

@app.get("/api/config")
async def get_config():
    """Get frontend configuration"""
    return {
        "useMockData": settings.USE_MOCK_DATA,
        "supportedModalities": ["liver-mri", "liver-ct", "ultrasound", "pathology"]
    }

@app.post("/api/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    modality: str = Form(...),
    patient_id: Optional[str] = Form(None)
):
    """Analyze medical image using Azure AI models"""
    try:
        if modality not in ["liver-mri", "liver-ct", "ultrasound", "pathology"]:
            raise HTTPException(status_code=400, detail="Invalid modality")
        
        image_data = await image.read()
        
        if len(image_data) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 50MB)")
        
        ai_service = get_ai_service()
        
        if patient_id:
            result = await ai_service.analyze_image_by_patient(patient_id, modality)
        else:
            result = await ai_service.analyze_image(image_data, modality)
        
        return {
            "success": True,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/upload-demo")
async def upload_demo_image(modality: str = Form(...), patient_id: Optional[str] = Form(None)):
    """Load a demo image for the specified modality"""
    try:
        if modality not in ["liver-mri", "liver-ct", "ultrasound", "pathology"]:
            raise HTTPException(status_code=400, detail="Invalid modality")
        
        from PIL import Image
        import nibabel as nib
        import numpy as np
        from pathlib import Path
        
        kaggle_data_path = Path(__file__).parent.parent.parent / "data" / "kaggle" / "liver-tumor" / "08-3D-Liver-Tumor-Segmentation" / "08-3D-Liver-Tumor-Segmentation" / "Task03_Liver_rs" / "images"
        
        if patient_id:
            patient_num = int(patient_id[1:])
            nifti_file = kaggle_data_path / f"liver_{patient_num}.nii"
            if not nifti_file.exists():
                raise HTTPException(status_code=404, detail=f"Patient file not found: liver_{patient_num}.nii")
        else:
            nifti_files = list(kaggle_data_path.glob("liver_*.nii"))
            if not nifti_files:
                raise HTTPException(status_code=404, detail="No liver scan files found in Kaggle dataset")
            nifti_file = nifti_files[0]
        
        nii_img = nib.load(str(nifti_file))
        data = nii_img.get_fdata()
        
        middle_slice = data.shape[2] // 2
        slice_data = data[:, :, middle_slice]
        
        slice_normalized = ((slice_data - slice_data.min()) / (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)
        
        img = Image.fromarray(slice_normalized, mode='L')
        img = img.convert('RGB')
        img = img.resize((800, 600), Image.Resampling.LANCZOS)
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "success": True,
            "message": f"Demo liver scan loaded from Kaggle dataset ({nifti_file.name})",
            "imageUrl": f"data:image/png;base64,{img_str}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo load failed: {str(e)}")

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data for dashboard"""
    return {
        "total_images": 1000,
        "accuracy_rate": 96.5,
        "modality_distribution": {
            "liver-mri": 350,
            "liver-ct": 420,
            "ultrasound": 180,
            "pathology": 50
        },
        "disease_distribution": {
            "Hepatocellular Carcinoma": 280,
            "Liver Cirrhosis": 220,
            "Fatty Liver Disease": 180,
            "Liver Metastases": 150,
            "Healthy Control": 170
        },
        "accuracy_over_time": [
            {"month": "Jan", "accuracy": 92.3},
            {"month": "Feb", "accuracy": 93.1},
            {"month": "Mar", "accuracy": 94.2},
            {"month": "Apr", "accuracy": 95.1},
            {"month": "May", "accuracy": 95.8},
            {"month": "Jun", "accuracy": 96.5}
        ]
    }

@app.get("/api/patients")
async def list_patients():
    """Get list of available patient IDs from NIfTI dataset"""
    try:
        from pathlib import Path
        
        nifti_dir = Path(__file__).parent.parent.parent / "data" / "kaggle" / "08-3D-Liver-Tumor-Segmentation" / "08-3D-Liver-Tumor-Segmentation" / "Task03_Liver_rs" / "images"
        
        if not nifti_dir.exists():
            raise HTTPException(status_code=404, detail="Dataset directory not found")
        
        nifti_files = sorted(nifti_dir.glob("liver_*.nii"))
        
        patients = []
        for f in nifti_files:
            patient_num = f.stem.split('_')[1]
            patients.append({
                'id': f"P{int(patient_num):03d}",
                'filename': f.name,
                'label': f"Patient {patient_num}"
            })
        
        return {
            'success': True,
            'patients': patients,
            'total': len(patients)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list patients: {str(e)}")

@app.post("/api/analyze/batch")
async def analyze_batch(
    patient_ids: str = Form(...),
    modality: str = Form(...)
):
    """Analyze multiple patients in serial (batch processing)"""
    try:
        if modality not in ["liver-mri", "liver-ct", "ultrasound", "pathology"]:
            raise HTTPException(status_code=400, detail="Invalid modality")
        
        ids = [id.strip() for id in patient_ids.split(',')]
        
        if len(ids) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 patients per batch")
        
        ai_service = get_ai_service()
        results = []
        
        for patient_id in ids:
            try:
                result = await ai_service.analyze_image_by_patient(patient_id, modality)
                results.append({
                    'patient_id': patient_id,
                    'success': True,
                    'data': result
                })
            except Exception as e:
                results.append({
                    'patient_id': patient_id,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'total': len(ids),
            'completed': len([r for r in results if r['success']]),
            'results': results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.get("/api/hip/patients")
async def list_hip_patients():
    """Get list of available hip CT scan patient IDs"""
    return {
        'success': True,
        'patients': [
            {'id': 'H001', 'label': 'Hip Patient 001', 'filename': 'hip_001.nii'},
            {'id': 'H002', 'label': 'Hip Patient 002', 'filename': 'hip_002.nii'},
            {'id': 'H003', 'label': 'Hip Patient 003', 'filename': 'hip_003.nii'},
        ],
        'total': 3
    }

@app.post("/api/hip/analyze")
async def analyze_hip(patient_id: str = Form(...)):
    """Analyze hip CT for replacement planning"""
    try:
        ai_service = get_ai_service()
        result = await ai_service.analyze_hip_image_by_patient(patient_id)
        
        return {
            'success': True,
            'data': result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hip analysis failed: {str(e)}")

@app.get("/api/hip/ct-images")
async def get_hip_ct_images():
    """Get hip CT scan images with red bone segmentation overlays"""
    try:
        from pathlib import Path
        
        ct_dir = Path(__file__).parent.parent / "data" / "hip_ct_scans"
        images = {}
        
        views = ["axial", "coronal", "sagittal", "3d_anterior", "3d_lateral", "3d_superior"]
        
        for view in views:
            b64_file = ct_dir / f"hip_ct_{view}.png.b64"
            if b64_file.exists():
                with open(b64_file, 'r') as f:
                    images[view] = f.read()
        
        return {
            'success': True,
            'images': images,
            'count': len(images)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load hip CT images: {str(e)}")

@app.get("/api/hip/demo-data")
async def get_hip_demo_data():
    """Get pre-loaded hip demo data for fast display"""
    return {
        'patient_id': 'H001',
        'segmentation': {
            'detected': ['Femur', 'Pelvis', 'Acetabulum'],
            'quality': 'Good bone quality',
            'femur_accuracy': 96.4,
            'pelvis_accuracy': 97.1,
            'acetabulum_accuracy': 95.8
        },
        'implantSizing': {
            'femoral_component': 'Size 4',
            'acetabular_component': 'Size 3',
            'polyethylene': '10mm'
        },
        'alignmentMetrics': {
            'mechanical_axis': '1.2° varus',
            'femoral_rotation': '3.0° external',
            'tibial_slope': '5.0° posterior'
        },
        'surgicalPlan': """**Preoperative Assessment:**
CT imaging demonstrates favorable anatomy for total hip arthroplasty with robotic-assisted precision. Bone quality assessment reveals adequate cortical thickness and trabecular density for cementless fixation. No significant acetabular dysplasia or proximal femoral deformity noted.

**Segmentation Results:**
- Femoral Head: 96.4% segmentation accuracy
- Acetabulum: 95.8% segmentation accuracy  
- Proximal Femur: 97.1% segmentation accuracy
- Native femoral offset: 45.2mm measured
- Leg length discrepancy: Minimal (<2mm)

**Implant Selection Recommendations:**
- Acetabular Component: 54mm press-fit cup, ceramic liner
- Femoral Component: Size 12 cementless metaphyseal-filling stem
- Bearing Surface: 32mm +5mm ceramic-on-ceramic with extended offset
- Planned restoration of anatomic offset and leg length

**Surgical Planning:**
- Approach: Posterior approach with enhanced soft tissue repair
- Target Acetabular Position: 42° inclination, 18° anteversion (within Lewinnek safe zone)
- Femoral Version: 10-15° anteversion planned
- Expected Leg Length Restoration: Equal bilateral limb lengths
- Predicted Range of Motion: Full flexion (>120°), unrestricted abduction

**Clinical Considerations:**
- Patient positioning: Lateral decubitus with robotic registration
- Intraoperative verification: Real-time implant positioning feedback
- Post-operative protocol: Standard weight-bearing as tolerated
- Follow-up imaging: 6-week and 1-year radiographic assessment

**Platform Compatibility:**
- ABC MedTech Robotic System ✓
- Major Surgical Planning Platforms ✓
- DICOM Export for OR Integration ✓""",
        'metrics': {
            'processingTime': '3.8min',
            'accuracy': '96.2%',
            'bonesSegmented': 4
        }
    }
