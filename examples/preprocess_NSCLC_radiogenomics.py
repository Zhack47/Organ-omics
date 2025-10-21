import os
import sys
from os.path import join
from tqdm import tqdm


# Path to the root of the directory containing
# the DICOM files for NSCLC Radiogenomics
root_dir = sys.argv[1]

patients_petct = 0
list_patients = [x for x in os.listdir(root_dir) if x!="LICENSE"]
for patient in tqdm(list_patients):
    patient_studies = os.listdir(join(root_dir, patient))
    num_studies = len(patient_studies)
    if num_studies<2:
        print(f"Found only {num_studies} for patient {patient}.")
    elif num_studies>2:
        print(f"Found {num_studies} for patient {patient}.")
        print("Select the ones you want to keep (format is 'x,y')(if none press 0):")
        for i, study_name in enumerate(patient_studies):
            print(f"({i+1}): {study_name}")
        input_ = input("?")
        if input_ == "0":
            pass
        else:
            values = list(map(int, input_.split(",")))
            assert len(values)==2
            patient_studies = [patient_studies[values[0]],
                               patient_studies[values[1]]]
    if len(patient_studies)== 2:
        print(f"Patient {patient} OK")
        patients_petct += 1
        

