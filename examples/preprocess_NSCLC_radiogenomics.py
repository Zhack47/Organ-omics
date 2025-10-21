import os
import sys
from os.path import join
from tqdm import tqdm
import SimpleITK as sitk


# Path to the root of the directory containing
# the DICOM files for NSCLC Radiogenomics
root_dir = sys.argv[1]

patients_petct = 0
list_patients = [x for x in os.listdir(root_dir) if x!="LICENSE"]
for patient in tqdm(list_patients):
    patient_studies = os.listdir(join(root_dir, patient, "CT")) + os.listdir(join(root_dir, patient, "PT"))
    num_studies = len(patient_studies)
    if num_studies!=2:  ## Found num_studies to only be 1 or 2 in the dataset
        print(f"Found {num_studies} for patient {patient}.")

    if len(patient_studies)== 2:
        patients_petct += 1
        for modality in ("PT", "CT"):
            for study in os.listdir(join(root_dir, patient, modality)):
                series = os.listdir(join(root_dir, patient, modality, study))
                for i, serie in enumerate(series):
                    reader = sitk.ImageSeriesReader()
                    reader.SetFileNames(reader.GetGDCMSeriesFileNames(
                        join(root_dir, patient, study, serie)
                    ))
                    image = reader.Execute()
                    sitk.WriteImage(image, join(root_dir, patient, modality, study, f"{serie}.nii.gz"))

print(f"Patients OK PET/CT: {patients_petct}")
