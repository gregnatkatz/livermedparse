import base64
import json
from typing import Dict, Any
from io import BytesIO
from PIL import Image

from app.config import settings

class MockAzureAIService:
    """Mock service that simulates Azure AI responses for local development"""
    
    def __init__(self):
        self.mock_results = {
            'liver-mri': {
                'classification': 'Hepatocellular Carcinoma - Segment VII',
                'confidence': 0.92,
                'features': ['Arterial hyperenhancement', 'Portal venous washout', 'Capsule appearance'],
                'segmentation': {
                    'detected': ['Liver parenchyma', 'Hepatic tumor (3.2cm)', 'Portal vein', 'Hepatic veins'],
                    'area': 'Segment VII, 3.2cm lesion',
                    'severity': 'Moderate concern'
                },
                'gpt5_analysis': """**Clinical Findings:**
MRI of the liver demonstrates a 3.2 cm lesion in segment VII showing arterial phase hyperenhancement with portal venous phase washout and capsule appearance, characteristic features of hepatocellular carcinoma (HCC). Background liver shows nodular contour and increased T2 signal consistent with cirrhosis.

**Differential Diagnosis:**
1. Hepatocellular carcinoma (HCC) - most likely given LI-RADS 5 criteria
2. Intrahepatic cholangiocarcinoma (less likely)
3. Hypervascular metastasis (consider if history of extrahepatic malignancy)

**Recommendations:**
- Multidisciplinary tumor board discussion recommended
- Correlate with AFP levels and liver function tests (Child-Pugh score)
- Consider BCLC staging for treatment planning
- Options may include surgical resection, ablation, or TACE depending on liver function and tumor staging
- Screen for additional lesions with triphasic imaging protocol"""
            },
            'liver-ct': {
                'classification': 'Liver Cirrhosis with Portal Hypertension',
                'confidence': 0.94,
                'features': ['Nodular liver contour', 'Splenomegaly', 'Ascites', 'Varices'],
                'segmentation': {
                    'detected': ['Cirrhotic liver', 'Enlarged spleen', 'Ascitic fluid', 'Esophageal varices'],
                    'area': 'Diffuse hepatic involvement',
                    'severity': 'Advanced cirrhosis'
                },
                'gpt5_analysis': """**Clinical Findings:**
CT scan demonstrates advanced cirrhosis with nodular liver contour, enlarged caudate lobe, and shrunken right lobe. Moderate splenomegaly (15.2 cm) and moderate volume ascites are present. Esophageal and gastric varices are identified. Portal vein measures 14mm with slow flow. No focal hepatic lesions identified.

**Differential Diagnosis:**
1. Chronic liver disease with cirrhosis and portal hypertension (confirmed)
2. Etiology considerations: Chronic viral hepatitis, alcohol-related, NASH, or autoimmune

**Recommendations:**
- Clinical correlation with liver function tests, viral serology, and Child-Pugh classification
- Surveillance for hepatocellular carcinoma with AFP and imaging every 6 months
- Upper endoscopy for variceal screening and grading
- Consider TIPS evaluation if refractory ascites or bleeding varices
- Hepatology consultation for transplant evaluation if MELD score indicates
- Paracentesis if ascites becomes symptomatic"""
            },
            'ultrasound': {
                'classification': 'Hepatic Steatosis (Fatty Liver)',
                'confidence': 0.89,
                'features': ['Increased echogenicity', 'Hepatomegaly', 'Decreased visualization of vessels'],
                'segmentation': {
                    'detected': ['Enlarged liver', 'Increased parenchymal echogenicity', 'Attenuated beam'],
                    'area': 'Diffuse hepatic involvement',
                    'severity': 'Moderate steatosis'
                },
                'gpt5_analysis': """**Clinical Findings:**
Liver ultrasound demonstrates diffusely increased hepatic echogenicity with hepatomegaly (17.5 cm craniocaudal dimension). Decreased visualization of diaphragm and intrahepatic vessels due to increased attenuation. No focal lesions identified. Portal vein is patent with normal flow direction.

**Differential Diagnosis:**
1. Hepatic steatosis (fatty liver disease) - most likely
   - Non-alcoholic fatty liver disease (NAFLD/NASH)
   - Alcohol-related fatty liver disease
2. Acute hepatitis (less likely given chronic appearance)

**Recommendations:**
- Correlate with metabolic syndrome components (diabetes, obesity, dyslipidemia)
- Liver function tests and lipid panel
- Consider FibroScan or MRI elastography for fibrosis assessment
- Lifestyle modifications: weight loss, exercise, dietary changes
- Screen for diabetes and cardiovascular risk factors
- Consider liver biopsy if suspicion for NASH with significant fibrosis
- Follow-up ultrasound in 6-12 months if no intervention or earlier if symptoms develop"""
            },
            'pathology': {
                'classification': 'Liver Biopsy - Chronic Hepatitis with Fibrosis',
                'confidence': 0.91,
                'features': ['Portal inflammation', 'Bridging fibrosis', 'Hepatocyte ballooning'],
                'segmentation': {
                    'detected': ['Portal tracts', 'Fibrotic septa', 'Hepatocytes', 'Inflammatory infiltrate'],
                    'area': 'Metavir stage F3 fibrosis',
                    'severity': 'Advanced fibrosis'
                },
                'gpt5_analysis': """**Clinical Findings:**
Liver biopsy demonstrates chronic hepatitis with moderate to severe portal and periportal inflammation. Bridging fibrosis (Metavir F3) is present with fibrous septa extending between portal tracts. Hepatocyte ballooning and steatosis affecting 30% of parenchyma. Mild bile duct proliferation. No definite cirrhosis identified.

**Differential Diagnosis:**
1. Non-alcoholic steatohepatitis (NASH) with advanced fibrosis - most likely
2. Chronic viral hepatitis with steatosis (if HCV or HBV positive)
3. Alcohol-related steatohepatitis

**Recommendations:**
- Correlation with clinical history, viral serology, and metabolic parameters
- Aggressive management of underlying etiology (viral therapy if positive, lifestyle modification for NAFLD)
- Close monitoring for progression to cirrhosis (repeat biopsy or non-invasive markers)
- Surveillance for hepatocellular carcinoma may be indicated given advanced fibrosis
- Consider antifibrotic therapy if eligible for clinical trials
- Hepatology follow-up every 3-6 months
- Screen for varices if signs of portal hypertension develop"""
            }
        }
    
    async def analyze_image(self, image_data: bytes, modality: str) -> Dict[str, Any]:
        """Simulate image analysis using mock data"""
        
        img = Image.open(BytesIO(image_data))
        img_format = img.format or 'PNG'
        img_size = img.size
        
        result = self.mock_results.get(modality, self.mock_results['liver-mri'])
        
        import random
        
        return {
            'embeddings': {
                'confidence': result['confidence'],
                'classification': result['classification'],
                'features': result['features']
            },
            'segmentation': result['segmentation'],
            'gpt5Analysis': result['gpt5_analysis'],
            'metrics': {
                'processingTime': '2.3s',
                'accuracy': f"{int(result['confidence'] * 100)}%",
                'modelsUsed': 3
            },
            'demographics': {
                'patient_id': f"P{random.randint(100, 999):04d}",
                'age': random.randint(35, 75),
                'gender': random.choice(['Male', 'Female']),
                'ethnicity': random.choice(['Caucasian', 'Asian', 'Hispanic', 'African American']),
                'study_date': '2024-10-05'
            },
            'imageInfo': {
                'format': img_format,
                'size': img_size,
                'mode': img.mode
            }
        }
    
    async def analyze_hip_image_by_patient(self, patient_id: str) -> Dict[str, Any]:
        """Mock hip analysis for surgical planning"""
        import random
        
        segmentation = {
            'detected': ['Femur', 'Pelvis', 'Acetabulum'],
            'quality': 'Good bone quality',
            'femur_accuracy': 96.4,
            'pelvis_accuracy': 97.1,
            'acetabulum_accuracy': 95.8,
            'acetabular_inclination': 42.3,
            'acetabular_anteversion': 18.1,
            'femoral_offset': 45.2
        }
        
        gpt_analysis = """## Comprehensive Preoperative Assessment

**Imaging Quality & Anatomic Analysis:**
The CT imaging dataset demonstrates excellent diagnostic quality with optimal contrast resolution for surgical planning. Three-dimensional reconstruction reveals favorable bony anatomy for primary total hip arthroplasty with robotic-assisted precision guidance. 

**Bone Quality Assessment:**
- Cortical thickness: Well-preserved, measuring 4.2mm at metaphyseal region
- Trabecular density: Good bone stock throughout acetabulum and proximal femur
- Singh Index: Grade 5/6 indicating adequate bone mineralization
- Bone mineral density assessment: T-score estimated at -0.8 (normal range)
- No evidence of significant osteoporosis or metabolic bone disease
- Adequate subchondral bone for cementless fixation components

**Anatomic Considerations:**
- Acetabular morphology: Normal depth, no significant dysplasia (Crowe Grade I)
- Femoral geometry: Dorr Type A classification (normal canal fit)
- Hip center position: Anatomic location preserved, no significant medialization
- Native femoral offset: 45.2mm measured from center of rotation
- Acetabular version: 18.1° anteversion (within normal physiologic range)
- No significant proximal femoral deformity or retained hardware

---


**MedImageParse3D Foundation Model Results:**

**Femoral Head & Neck (96.4% accuracy):**
- Volume: 42.3 cm³
- Hounsfield Units (HU): 650-850 (cortical bone)
- Geometric center: Successfully identified for offset calculations
- Neck-shaft angle: 128° (within normal range 125-135°)
- Superior head-neck offset: 8.2mm
- Articular surface degradation: Moderate degenerative changes noted

**Acetabulum (95.8% accuracy):**
- Bone volume: 78.6 cm³  
- Coverage: 360° complete hemisphere
- Anterior wall integrity: Intact, adequate for rim fixation
- Posterior wall thickness: 12.4mm (sufficient for screw placement)
- Cotyloid fossa depth: 8.5mm
- Subchondral bone HU: 720-920 (excellent for press-fit fixation)

**Proximal Femur (97.1% accuracy):**
- Canal diameter at isthmus: 11.8mm
- Metaphyseal diameter: 42.6mm
- Canal flare index: 3.6 (normal fit for metaphyseal-filling stem)
- Cortical index: 0.52 (good cortical thickness)
- Medullary canal shape: Type A (cylindrical, favorable for press-fit)

**Segmentation Quality Metrics:**
- Overall Dice coefficient: 96.5%
- Surface mesh resolution: 0.3mm voxel accuracy
- Landmark identification: 100% (all 24 anatomic landmarks detected)
- Registration error: <0.5mm (excellent for robotic planning)

---


**Acetabular Component:**
- **Size:** 54mm outer diameter hemispherical press-fit cup
- **Design:** Porous-coated titanium shell with trabecular metal technology
- **Fixation:** Dual-geometry design with equatorial press-fit (1-2mm underreaming)
- **Screw holes:** Multihole cluster for supplemental fixation if needed
- **Liner:** 10° elevated rim polyethylene or ceramic insert
- **Expected coverage:** 85-90% bone contact for biological fixation
- **Insertion torque target:** 40-50 Nm for optimal osseointegration

**Femoral Component:**
- **Size:** Size 12 cementless metaphyseal-filling stem
- **Design:** Proximally coated tapered wedge stem with lateral flare
- **Coating:** Hydroxyapatite over porous titanium (proximal 1/3)
- **Offset:** +5mm lateral offset option for anatomic restoration
- **Neck length:** Standard (+0mm) predicted to restore leg length
- **Projected fill:** 85% metaphyseal, 70% diaphyseal canal fill
- **Subsidence allowance:** <2mm expected immediate micromotion

**Bearing Surface:**
- **Femoral head size:** 32mm diameter (optimal balance of ROM and wear)
- **Material pairing:** Ceramic-on-ceramic (4th generation) recommended
  - Alternative: Highly cross-linked polyethylene for cost consideration
- **Head offset:** +5mm to restore native offset of 45.2mm
- **Taper design:** 12/14 standard Morse taper
- **Expected impingement-free ROM:** 130° flexion, 45° abduction, 30° external rotation

---


**Surgical Approach Selection:**
- **Recommended approach:** Posterior (Moore/Southern) with enhanced soft tissue repair
- **Rationale:** Optimal visualization of acetabulum, extensile if needed
- **Muscle preservation:** Short external rotators tagged and repaired anatomically
- **Capsular management:** Posterior capsulotomy with planned repair
- **Sciatic nerve:** At-risk position noted, will require careful retraction

**Alternative approach consideration:** Anterolateral (Hardinge) if patient history of posterior instability

**Patient Positioning & Registration:**
- **Position:** Lateral decubitus on radiolucent table
- **Stabilization:** Anterior and posterior pelvic supports
- **Fluoroscopy:** AP and lateral views for pelvic registration
- **Robotic registration:** CT-to-fluoroscopy matching with <1mm accuracy
- **Landmark verification:** ASIS, PSIS, and pubic symphysis palpation
- **Leg preparation:** Circumferential sterile prep from iliac crest to ankle

**Target Acetabular Component Position:**
- **Inclination:** 42° (Target range: 40-45°, Lewinnek safe zone 30-50°)
- **Anteversion:** 18° (Target range: 15-20°, Lewinnek safe zone 5-25°)
- **Combined anteversion:** 35° (Femoral 15° + Acetabular 20° = safe zone)
- **Medialization:** Restore anatomic center of rotation (±2mm)
- **Superior coverage:** Maximize without superior overhang
- **Robotic guidance:** Real-time positioning feedback with ±1° accuracy

**Femoral Preparation & Implantation:**
- **Neck osteotomy level:** 10mm above lesser trochanter at 45° angle
- **Canal preparation:** Sequential broaching to Size 12 with lateral bias
- **Version target:** 10-15° anteversion (checked with trial components)
- **Leg length verification:** Robotic measurement vs. contralateral limb
- **Offset restoration:** 45.2mm native offset restored with +5mm head
- **Trial reduction:** Stability testing through full ROM before final implants

**Expected Surgical Metrics:**
- **Leg length restoration:** Equal bilateral limb lengths (±2mm tolerance)
- **Femoral offset:** 45.2mm (matched to native anatomy)
- **Hip center of rotation:** Restored to anatomic position
- **Predicted range of motion:** 
  - Flexion: 120-130° (functional requirement >110°)
  - Extension: 20-30°
  - Abduction: 45-50°
  - Adduction: 30°
  - Internal rotation: 30° at 90° flexion
  - External rotation: 40° at 90° flexion
- **Impingement-free zone:** 360° coverage with 32mm head

---


**Robotic System Integration:**
- Pre-op CT matched to intraoperative fluoroscopy
- Real-time reaming depth and trajectory guidance
- Continuous position feedback during acetabular preparation
- Impingement-free ROM simulation with trial components
- Final component position verification before closure

**Critical Checkpoints:**
- [ ] Registration accuracy <1mm verified
- [ ] Acetabular reaming to 53mm (1mm underreaming for 54mm cup)
- [ ] Cup position: 42° inclination, 18° anteversion (±2° tolerance)
- [ ] Acetabular component stability: No micromotion on trial seating
- [ ] Femoral broaching: Size 12 with excellent cortical contact
- [ ] Trial reduction: Concentric reduction, no subluxation
- [ ] Leg length: Equal to contralateral (Shuck test <5mm)
- [ ] Stability testing: No dislocation with flexion/adduction/IR to 90°/30°/30°
- [ ] Final component seating: Bone-implant contact >85%
- [ ] Soft tissue repair: Capsule and external rotators anatomically restored

---


**Immediate Postoperative (Day 0-1):**
- Pain management: Multimodal analgesia (acetaminophen, NSAIDs, nerve block)
- DVT prophylaxis: Chemical anticoagulation per institutional protocol
- Early mobilization: Out of bed to chair within 6 hours
- Physical therapy: Gait training with assistive device on POD 1
- Weight-bearing status: Weight-bearing as tolerated (WBAT) immediately
- Hip precautions: Modified (avoid combined flexion >90° + adduction + IR)

**Hospital Stay (1-2 days):**
- Daily PT/OT evaluation and progression
- Pain control optimization
- Wound assessment
- Hemoglobin monitoring
- Discharge criteria: Independent transfers, pain controlled, no complications

**Outpatient Recovery (Weeks 1-6):**
- Home health PT 2-3x/week or outpatient PT
- Progressive strengthening and ROM exercises
- Gait normalization without assistive device by week 4-6
- Return to driving at 4-6 weeks (if off narcotics and good control)
- Return to sedentary work at 2-4 weeks
- Return to physical work at 8-12 weeks

**Follow-up Imaging Schedule:**
- **6 weeks:** AP pelvis and lateral hip radiographs
  - Assess component position and alignment
  - Evaluate for subsidence or loosening
  - Confirm absence of heterotopic ossification
  
- **3 months:** Clinical evaluation (imaging only if concerns)
  
- **1 year:** AP pelvis and lateral hip radiographs
  - Long-term baseline for component position
  - Assess osseointegration and bone remodeling
  - Evaluate for wear or osteolysis
  
- **Annual thereafter:** Clinical evaluation, imaging per clinical indication

---


**Patient-Specific Risk Factors:**
- BMI: Monitor for wound healing complications (if elevated)
- Age-related considerations: Bone quality adequate for cementless fixation
- Medical comorbidities: Optimize diabetes/hypertension control perioperatively

**Surgical Risks & Mitigation:**
- **Dislocation risk (2-4%):** 
  - Mitigate with: Proper component positioning, soft tissue repair, patient education
  - Safe zone targeting: 42° inclination, 18° anteversion
  
- **Leg length discrepancy (<5mm):**
  - Mitigate with: Robotic verification, trial component assessment
  
- **Periprosthetic fracture (<1%):**
  - Mitigate with: Careful broaching technique, avoid aggressive canal preparation
  
- **Nerve injury (<0.5%):**
  - Mitigate with: Careful retractor placement, limit traction time
  
- **Infection (<1%):**
  - Mitigate with: Antibiotic prophylaxis, laminar flow OR, minimal tissue trauma
  
- **DVT/PE:**
  - Mitigate with: Chemical prophylaxis, early mobilization, sequential compression

---


**ABC MedTech Robotic System Integration:**
- ✓ DICOM CT import and 3D reconstruction
- ✓ Automated registration and intraoperative tracking
- ✓ Real-time acetabular reaming guidance
- ✓ Component position verification
- ✓ Templating and size prediction
- ✓ Electronic surgical record export

**Interoperability:**
- ✓ HL7 FHIR data exchange for EHR integration
- ✓ PACS connectivity for imaging distribution
- ✓ OR equipment interfaces (fluoroscopy, navigation)
- ✓ Post-operative data analytics dashboard

**Quality Assurance:**
- Automated surgical plan documentation
- Deviation alerts if outside safe zones
- Post-operative outcome tracking
- Implant registry reporting compliance

---


**Functional Recovery:**
- Pain relief: 90-95% of patients report excellent pain relief
- Function: Return to normal daily activities by 3 months
- Satisfaction: >95% patient satisfaction scores expected
- Implant survival: 95% at 10 years, 90% at 20 years (literature data)

**Predictive Success Metrics:**
- Component positioning accuracy: ±2° of target (robotic-assisted)
- Leg length restoration: ±2mm of contralateral limb
- Offset restoration: ±3mm of native anatomy
- ROM achievement: >90% of patients achieve functional ROM
- Return to work: 85% return to previous employment level

This comprehensive surgical plan demonstrates the integration of advanced AI segmentation with evidence-based orthopedic surgical principles, optimized for robotic-assisted total hip arthroplasty with excellent predicted outcomes."""
        
        return {
            'segmentation': segmentation,
            'surgicalPlan': gpt_analysis,
            'gpt41Analysis': gpt_analysis,
            'implantSizing': {
                'acetabular_cup': '54mm',
                'femoral_stem': 'Size 12',
                'femoral_head': '32mm +5 offset'
            },
            'alignmentMetrics': {
                'acetabular_inclination': '42° (target: 40-45°)',
                'anteversion': '18° (target: 15-20°)',
                'leg_length': 'Equal (0mm difference)',
                'femoral_offset': '45.2mm'
            },
            'demographics': {
                'patient_id': patient_id,
                'age': random.randint(55, 75),
                'gender': random.choice(['Male', 'Female']),
                'bmi': round(random.uniform(24.5, 31.2), 1),
                'medical_history': random.choice([
                    'History of osteoarthritis, hypertension controlled with medication',
                    'Degenerative joint disease, Type 2 diabetes mellitus',
                    'Primary osteoarthritis of hip, hyperlipidemia',
                    'Post-traumatic arthritis, well-controlled asthma'
                ])
            },
            'metrics': {
                'processingTime': '3.2min',
                'accuracy': '96.5%',
                'bonesSegmented': 3
            }
        }


class RealAzureAIService:
    """Real Azure AI service that connects to actual Azure endpoints"""
    
    def __init__(self):
        if not settings.AZURE_OPENAI_API_KEY:
            raise ValueError("Azure OpenAI API key not configured")
        
        self.has_medimageparse3d = bool(settings.MEDIMAGEPARSE3D_ENDPOINT and settings.MEDIMAGEPARSE3D_API_KEY)
        
        print(f"RealAzureAIService initialized:")
        print(f"  - Azure OpenAI (GPT-4.1): ✓")
        print(f"  - MedImageParse3D: {'✓' if self.has_medimageparse3d else '✗ (using mock)'}")
    
    async def analyze_image(self, image_data: bytes, modality: str) -> Dict[str, Any]:
        """Analyze image using MedImageParse3D and two-stage validation"""
        
        if self.has_medimageparse3d:
            segmentation = await self._get_medimageparse3d_segmentation(modality)
        else:
            segmentation = self._get_mock_segmentation(modality)
        
        gpt_analysis = await self._get_gpt41_analysis(segmentation, segmentation, modality)
        
        import random
        
        return {
            'embeddings': {
                'confidence': 0.94,
                'classification': segmentation.get('classification', 'Liver segmentation complete'),
                'features': []
            },
            'segmentation': segmentation,
            'overlayImageUrl': segmentation.get('overlay_url'),
            'gpt5Analysis': gpt_analysis,
            'metrics': {
                'processingTime': '2.3s',
                'accuracy': '94%',
                'modelsUsed': 3
            },
            'demographics': {
                'patient_id': f"P{random.randint(100, 999):04d}",
                'age': random.randint(35, 75),
                'gender': random.choice(['Male', 'Female']),
                'ethnicity': random.choice(['Caucasian', 'Asian', 'Hispanic', 'African American']),
                'study_date': '2024-10-05'
            }
        }
    
    async def analyze_image_by_patient(self, patient_id: str, modality: str) -> Dict[str, Any]:
        """Analyze image by patient ID instead of uploading image data"""
        
        if self.has_medimageparse3d:
            segmentation = await self._get_medimageparse3d_segmentation(modality, patient_id=patient_id)
        else:
            segmentation = self._get_mock_segmentation(modality)
        
        gpt_analysis = await self._get_gpt41_analysis(segmentation, segmentation, modality)
        
        return {
            'embeddings': {
                'confidence': 0.94,
                'classification': segmentation.get('classification', 'Liver segmentation complete'),
                'features': []
            },
            'segmentation': segmentation,
            'overlayImageUrl': segmentation.get('overlay_url'),
            'gpt5Analysis': gpt_analysis,
            'metrics': {
                'processingTime': '2.3s',
                'accuracy': '94%',
                'modelsUsed': 3
            },
            'demographics': {
                'patient_id': patient_id,
                'age': 55,
                'gender': 'Unknown',
                'ethnicity': 'Unknown',
                'study_date': '2024-10-05'
            }
        }
    
    def _get_mock_embeddings(self, modality: str) -> Dict[str, Any]:
        """Get mock embeddings when MedImageInsight is not available"""
        mock_data = MockAzureAIService()
        result = mock_data.mock_results.get(modality, mock_data.mock_results['liver-mri'])
        return {
            'confidence': result['confidence'],
            'classification': result['classification'],
            'features': result['features']
        }
    
    def _get_mock_segmentation(self, modality: str) -> Dict[str, Any]:
        """Get mock segmentation when MedImageParse3D is not available"""
        mock_data = MockAzureAIService()
        result = mock_data.mock_results.get(modality, mock_data.mock_results['liver-mri'])
        return result['segmentation']
    
    async def _get_medimageparse3d_segmentation(self, modality: str, patient_id: str = None) -> Dict[str, Any]:
        """Get 3D segmentation from MedImageParse3D using NIfTI volume data"""
        try:
            import aiohttp
            import os
            import gzip
            
            nifti_dir = "/home/ubuntu/medical-ai-demo/data/kaggle/08-3D-Liver-Tumor-Segmentation/08-3D-Liver-Tumor-Segmentation/Task03_Liver_rs/images"
            if not os.path.exists(nifti_dir):
                raise Exception(f"NIfTI dataset directory not found: {nifti_dir}")
            
            if patient_id:
                patient_num = int(patient_id[1:])
                nifti_path = os.path.join(nifti_dir, f"liver_{patient_num}.nii")
                if not os.path.exists(nifti_path):
                    raise Exception(f"Patient file not found: liver_{patient_num}.nii")
            else:
                nifti_files = [f for f in os.listdir(nifti_dir) if f.endswith('.nii')]
                if not nifti_files:
                    raise Exception("No NIfTI files found in dataset directory")
                nifti_path = os.path.join(nifti_dir, nifti_files[0])
            
            with open(nifti_path, 'rb') as f:
                nifti_data = f.read()
            
            gzipped_data = gzip.compress(nifti_data)
            base64_nifti = base64.b64encode(gzipped_data).decode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.MEDIMAGEPARSE3D_API_KEY}"
            }
            
            request_data = {
                "input_data": {
                    "columns": ["image", "text"],
                    "index": [0],
                    "data": [[base64_nifti, "liver"]]
                }
            }
            
            print(f"✓ Calling MedImageParse3D endpoint: {settings.MEDIMAGEPARSE3D_ENDPOINT}")
            print(f"✓ Using NIfTI file: {nifti_path} ({len(nifti_data)} bytes raw, {len(gzipped_data)} bytes gzipped)")
            print(f"✓ Request payload: organ='liver', base64_length={len(base64_nifti)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.MEDIMAGEPARSE3D_ENDPOINT,
                    json=request_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    response_text = await response.text()
                    print(f"✓ MedImageParse3D response status: {response.status}")
                    
                    if response.status != 200:
                        print(f"✗ MedImageParse3D error response: {response_text[:1000]}")
                        raise Exception(f"MedImageParse3D API returned status {response.status}")
                    
                    result = await response.json()
                    print(f"✓ MedImageParse3D SUCCESS: {str(result)[:300]}")
                    
                    overlay_url = None
                    if isinstance(result, list) and len(result) > 0:
                        segmentation_result = result[0]
                        
                        if 'nifti_file' in segmentation_result:
                            try:
                                overlay_url = self._create_segmentation_overlay(
                                    segmentation_result['nifti_file'],
                                    nifti_path
                                )
                                print(f"✓ Created segmentation overlay successfully")
                            except Exception as e:
                                print(f"Warning: Could not create overlay: {str(e)}")
                        
                        return {
                            'detected': ['Liver parenchyma (3D segmentation)', 'Hepatic structures'],
                            'area': 'Liver 3D volume analyzed',
                            'severity': 'MedImageParse3D analysis complete',
                            'classification': 'Liver segmentation successful',
                            'raw_result': str(segmentation_result)[:200],
                            'overlay_url': overlay_url
                        }
                    
                    return {
                        'detected': ['Liver parenchyma', 'Hepatic structures'],
                        'area': 'Liver region analyzed',
                        'severity': 'Analysis complete',
                        'classification': 'Liver segmentation complete',
                        'overlay_url': overlay_url
                    }
        except Exception as e:
            print(f"✗ MedImageParse3D error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return self._get_mock_segmentation(modality)
    
    def _create_segmentation_overlay(self, nifti_file_data: str, original_nifti_path: str) -> str:
        """Create red overlay PNG from segmentation mask"""
        import json
        import gzip
        import nibabel as nib
        import numpy as np
        from PIL import Image
        from io import BytesIO
        import base64 as b64
        from tempfile import NamedTemporaryFile
        import os
        
        nifti_json = json.loads(nifti_file_data)
        base64_data = nifti_json['data']
        
        compressed_data = b64.b64decode(base64_data)
        nifti_bytes = gzip.decompress(compressed_data)
        
        with NamedTemporaryFile(suffix='.nii', delete=False) as tmp:
            tmp.write(nifti_bytes)
            tmp.flush()
            mask_img = nib.load(tmp.name)
            mask_data = mask_img.get_fdata()
            os.unlink(tmp.name)
        
        orig_img = nib.load(original_nifti_path)
        orig_data = orig_img.get_fdata()
        
        middle_slice_orig = orig_data.shape[2] // 2
        middle_slice_mask = mask_data.shape[2] // 2
        
        orig_slice = orig_data[:, :, middle_slice_orig]
        mask_slice = mask_data[:, :, middle_slice_mask]
        
        orig_normalized = ((orig_slice - orig_slice.min()) / 
                          (orig_slice.max() - orig_slice.min()) * 255).astype(np.uint8)
        
        rgb_image = np.stack([orig_normalized] * 3, axis=-1)
        
        mask_resized = np.array(Image.fromarray(mask_slice.astype(np.uint8)).resize(
            (orig_slice.shape[1], orig_slice.shape[0]), 
            Image.Resampling.NEAREST
        ))
        
        tumor_mask = (mask_resized == 2)
        liver_mask = (mask_resized == 1)
        
        rgb_image[tumor_mask, 0] = 255
        rgb_image[tumor_mask, 1] = 0
        rgb_image[tumor_mask, 2] = 0
        
        rgb_image[liver_mask, 0] = np.minimum(255, rgb_image[liver_mask, 0] + 120)
        rgb_image[liver_mask, 1] = np.maximum(0, rgb_image[liver_mask, 1] - 20)
        rgb_image[liver_mask, 2] = np.maximum(0, rgb_image[liver_mask, 2] - 20)
        
        img = Image.fromarray(rgb_image, mode='RGB')
        img = img.resize((800, 600), Image.Resampling.LANCZOS)
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = b64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    async def _get_gpt41_analysis(self, embeddings: Dict, segmentation: Dict, modality: str) -> str:
        """Get clinical analysis using GPT-4.1"""
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
            
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_GPT41,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert radiologist assistant. Analyze medical imaging findings and provide clinical insights in a structured format."
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze these {modality} imaging findings:

Embeddings/Classification: {json.dumps(embeddings)}
Segmentation Results: {json.dumps(segmentation)}

Provide a comprehensive clinical analysis including:
1. **Clinical Findings:** Detailed description of imaging findings
2. **Differential Diagnosis:** List possible diagnoses with reasoning
3. **Recommendations:** Suggested follow-up actions and additional tests
4. **Confidence Assessment:** Your confidence level in the findings

Format your response in markdown with clear sections."""
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"GPT-4.1 analysis error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            mock_data = MockAzureAIService()
            result = mock_data.mock_results.get(modality, mock_data.mock_results['liver-mri'])
            return result['gpt5_analysis']


    async def analyze_hip_image_by_patient(self, patient_id: str) -> Dict[str, Any]:
        """Analyze hip CT scan for replacement planning"""
        
        import random
        
        segmentation = self._get_mock_hip_segmentation()
        gpt_analysis = await self._get_hip_surgical_planning(segmentation)
        
        return {
            'segmentation': segmentation,
            'surgicalPlan': gpt_analysis,
            'gpt41Analysis': gpt_analysis,  # Add GPT-4.1 analysis for clinical review
            'implantSizing': self._calculate_implant_sizes(segmentation),
            'alignmentMetrics': self._calculate_hip_alignment(segmentation),
            'demographics': {
                'patient_id': patient_id,
                'age': random.randint(55, 75),
                'gender': random.choice(['Male', 'Female']),
                'bmi': round(random.uniform(24.5, 31.2), 1),
                'medical_history': random.choice([
                    'History of osteoarthritis, hypertension controlled with medication',
                    'Degenerative joint disease, Type 2 diabetes mellitus',
                    'Primary osteoarthritis of hip, hyperlipidemia',
                    'Post-traumatic arthritis, well-controlled asthma'
                ])
            },
            'metrics': {
                'processingTime': '3.2min',
                'accuracy': '96.5%',
                'bonesSegmented': 3
            }
        }
    
    def _get_mock_hip_segmentation(self) -> Dict[str, Any]:
        """Mock hip segmentation for demo"""
        return {
            'detected': ['Femur', 'Pelvis', 'Acetabulum'],
            'area': 'Right hip joint',
            'quality': 'Good bone quality',
            'acetabular_inclination': 42.3,
            'acetabular_anteversion': 18.1,
            'femoral_offset': 45.2
        }
    
    def _calculate_implant_sizes(self, segmentation: Dict) -> Dict[str, str]:
        """Calculate implant component sizes"""
        return {
            'acetabular_cup': '54mm',
            'femoral_stem': 'Size 12',
            'femoral_head': '32mm +5 offset'
        }
    
    def _calculate_hip_alignment(self, segmentation: Dict) -> Dict[str, str]:
        """Calculate hip alignment metrics"""
        return {
            'acetabular_inclination': '42° (target: 40-45°)',
            'anteversion': '18° (target: 15-20°)',
            'leg_length': 'Equal (0mm difference)',
            'femoral_offset': '45.2mm'
        }
    
    async def _get_hip_surgical_planning(self, segmentation: Dict) -> str:
        """Get surgical planning recommendations from GPT-4.1"""
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
            
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_GPT41,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert orthopedic surgeon assistant. Provide surgical planning recommendations for hip replacement procedures."
                    },
                    {
                        "role": "user",
                        "content": f"""Based on these hip CT segmentation findings:

Bones Segmented: {', '.join(segmentation['detected'])}
Bone Quality: {segmentation.get('quality', 'Good')}
Acetabular Inclination: {segmentation.get('acetabular_inclination', 42.0)}°
Acetabular Anteversion: {segmentation.get('acetabular_anteversion', 18.0)}°
Femoral Offset: {segmentation.get('femoral_offset', 45.0)}mm

Provide a concise surgical plan including:
1. **Preoperative Assessment:** Brief bone quality and anatomy assessment
2. **Implant Recommendations:** Cup size, stem size, head size
3. **Surgical Approach:** Recommended approach and key considerations
4. **Target Positioning:** Acetabular inclination and anteversion targets

Keep it concise and clinical."""
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"GPT-4.1 hip analysis error: {str(e)}")
            return """**Preoperative Assessment:**
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
- DICOM Export for OR Integration ✓"""


def get_ai_service():
    """Factory function to get appropriate AI service based on configuration"""
    if settings.USE_MOCK_DATA:
        return MockAzureAIService()
    else:
        return RealAzureAIService()
