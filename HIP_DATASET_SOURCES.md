# Hip CT Dataset Sources

## Open Datasets for Hip Replacement Planning (500+ CT Scans)

### 1. TCIA - The Cancer Imaging Archive

#### PELVIC-REFERENCE-DATA Collection
- **URL**: https://www.cancerimagingarchive.net/collection/pelvic-reference-data/
- **Description**: CT and CBCT images of pelvic anatomy
- **Format**: DICOM
- **Access**: Free, public
- **Estimated Size**: 50-100 patients

#### CT-ORG Dataset
- **URL**: https://www.cancerimagingarchive.net/collection/ct-org/
- **Description**: 140 CT scans with labeled organs including pelvis/hip bones
- **Format**: DICOM with segmentation masks
- **Access**: Free, requires data usage agreement
- **Size**: 140 patients ✓

### 2. Kaggle Datasets

#### Hip Fracture CT Scans
- **Search**: "hip CT" on Kaggle
- **Potential datasets**:
  - RSNA 2018 Cervical Spine Fracture Detection (includes pelvis)
  - Various orthopedic imaging competitions
  
### 3. Medical Segmentation Decathlon
- **URL**: http://medicaldecathlon.com/
- **Task**: May include pelvic/hip segmentation tasks
- **Format**: NIfTI
- **Access**: Free registration

### 4. Grand Challenge
- **URL**: https://grand-challenge.org/
- **Search**: "hip" OR "pelvis" OR "femur"
- **Multiple competitions** with CT data

### 5. OpenNeuro / NITRC
- **NITRC URL**: https://www.nitrc.org/
- **Focus**: Neuroimaging but some include pelvis scans
- **Format**: NIfTI, DICOM

### 6. Radiopaedia
- **URL**: https://radiopaedia.org/
- **Cases**: Individual teaching cases with hip CTs
- **Access**: Free for educational use
- **Quantity**: 100s of individual cases

## Recommended Approach for 500+ Dataset

### Option A: Combine Multiple Sources (Recommended)
1. **CT-ORG** (140 scans) - TCIA
2. **PELVIC-REFERENCE-DATA** (50-100 scans) - TCIA
3. **Medical Segmentation Decathlon** (50-100 scans if available)
4. **Grand Challenge datasets** (200+ scans from various competitions)
5. **Radiopaedia teaching cases** (100+ individual cases)

**Total**: 500-640 scans

### Option B: Mock Dataset for Demo
For rapid prototyping and demo purposes:
- Use 10-20 representative samples from TCIA
- Generate synthetic variations
- Focus on quality over quantity for demo

## Data Download Instructions

### TCIA Download
```bash
# Install TCIA downloader
pip install tcia-utils

# Download PELVIC-REFERENCE-DATA
from tcia_utils import nbia
nbia.getCollectionPatientList("PELVIC-REFERENCE-DATA")
```

### Format Conversion
```python
# Convert DICOM to NIfTI (compatible with MedImageParse3D)
import nibabel as nib
import pydicom
from pydicom.data import get_testdata_files

# Load DICOM series
# Convert to NIfTI
# Save for processing
```

## For Demo - Quick Start

1. **Download 10 samples** from TCIA PELVIC-REFERENCE-DATA
2. **Convert to NIfTI** format
3. **Process with MedImageParse3D** to create pre-segmented results
4. **Store results** as JSON for fast demo loading

This provides realistic demo without needing full 500-scan dataset immediately.

## Production Deployment

For Stryker production:
1. Use Stryker's proprietary Mako dataset
2. Fine-tune MedImageParse3D on their annotated data
3. Validate against their gold standard
4. Deploy with their clinical workflow

---

**Next Steps**:
1. Download TCIA samples (10-20 for demo)
2. Process with MedImageParse3D
3. Build UI with pre-loaded results
4. Scale to full 500+ dataset as needed
