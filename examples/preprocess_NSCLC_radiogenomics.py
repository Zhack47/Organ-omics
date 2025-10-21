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
    try:
        studies_CT = os.listdir(join(root_dir, patient, "CT"))
    except:
        studies_CT = []
    try:
        studies_PT = os.listdir(join(root_dir, patient, "PT"))
    except:
        studies_PT = []
    num_studies = len(studies_CT)+len(studies_PT)

    if studies_PT and studies_CT:
        patients_petct += 1
        for modality in ("PT", "CT"):
            for study in os.listdir(join(root_dir, patient, modality)):
                series = os.listdir(join(root_dir, patient, modality, study))
                for i, serie in enumerate(series):
                    pass
                    '''reader = sitk.ImageSeriesReader()
                    reader.SetFileNames(reader.GetGDCMSeriesFileNames(
                        join(root_dir, patient, modality, study, serie)
                    ))
                    image = reader.Execute()
                    sitk.WriteImage(image, join(root_dir, patient, modality, study, f"{serie}.nii.gz"))'''
    else:
        print(f"Found {num_studies} for patient {patient}.")

print(f"Patients OK PET/CT: {patients_petct}")
