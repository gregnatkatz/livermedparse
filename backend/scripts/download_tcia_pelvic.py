#!/usr/bin/env python3
"""Download sample patient CT scans from TCIA PELVIC-REFERENCE-DATA collection"""

from tcia_utils import nbia
import os

download_dir = "/home/ubuntu/livermedparse/backend/data/pelvic_ct_patients"
os.makedirs(download_dir, exist_ok=True)

print("=" * 70)
print("Downloading PELVIC-REFERENCE-DATA from TCIA")
print("High-quality full-patient pelvic CT scans")
print("=" * 70)
print()

collection = "PELVIC-REFERENCE-DATA"

print(f"Fetching patient list from {collection}...")
try:
    patients = nbia.getPatient(collection=collection, format="df")
    print(f"Found {len(patients)} patients in collection")
    print()
    
    num_samples = min(5, len(patients))
    print(f"Downloading {num_samples} sample patients for demo...")
    print()
    
    for i in range(num_samples):
        patient_id = patients.iloc[i]['PatientID']
        print(f"[{i+1}/{num_samples}] Downloading patient: {patient_id}")
        
        try:
            nbia.downloadSeries(
                series_data=patient_id,
                input_type="patientId",
                path=download_dir,
                csv_filename=f"patient_{i+1}_manifest.csv"
            )
            print(f"  ✓ Downloaded to {download_dir}/{patient_id}/")
        except Exception as e:
            print(f"  ✗ Error downloading {patient_id}: {e}")
        print()
    
    print(f"\n✅ Downloaded {num_samples} sample patients!")
    print(f"Location: {download_dir}/")
    print("\nThese are full-patient pelvic CT scans with:")
    print("  - Visible soft tissue (muscles, fat, organs)")
    print("  - Hip and pelvic bones")
    print("  - DICOM format ready for processing")
    
except Exception as e:
    print(f"Error accessing TCIA: {e}")
    print("\nNote: TCIA may require authentication for bulk downloads.")
    print("Alternative: Use the NBIA Data Retriever from their website.")
