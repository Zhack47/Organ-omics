import os
import sys
import warnings
import pydicom
from os.path import join
from tqdm import tqdm
import SimpleITK as sitk
from math import exp, log
from pydicom.tag import Tag
from datetime import datetime



def parse_datetime(date_time: str) -> datetime:
    """class method to parse date time

    Args:
        date_time (str): [date and time in  "%Y%m%d%H%M%S" format ]

    Returns:
        [datetime]: [return parsed datetime]]
    """
    # remove microsecond at it is inconstant over dicom
    if '.' in date_time:
        date_time = date_time[0: date_time.index('.')]
    # parse datetime to date objet
    return datetime.strptime(date_time, "%Y%m%d%H%M%S")



def find_factor(dicom, logger=None):
    """
        Calcul of  SUV factor
    """

    patient_name = dicom[Tag(0x00100010)].value  # For debug / logging purposes
    units = dicom[Tag(0x00541001)].value
    known_units = ['GML', 'BQML', 'CNTS']

    if units not in known_units:
        logger.info(f'Unknown PET Units: {units}')
        print(f'Patient {patient_name}: Unknown PET Units: {units}')

    if units == 'GML':
        return 1

    if units == 'CNTS':
        if Tag(0x70531000) in dicom:
            philips_suv_factor = dicom[Tag(0x70531000)].value
            return philips_suv_factor
        else:
            print('Missing Philips private Factors')

    if dicom[Tag(0x00101030)].value != None:
        patient_weight = dicom[Tag(0x00101030)].value * 1000  # kg to g conversion
    else:
        patient_weight = 74 * 1000

    series_time = dicom[Tag(0x00080031)].value
    series_date = dicom[Tag(0x00080021)].value
    series_datetime = series_date + series_time

    series_datetime = parse_datetime(series_datetime)

    acquisition_time = dicom[Tag(0x00080032)].value
    acquisition_date = dicom[Tag(0x00080022)].value
    acquisition_datetime = acquisition_date + acquisition_time

    acquisition_datetime = parse_datetime(acquisition_datetime)

    decay_correction = dicom[Tag(0x00541102)].value

    radionuclide_half_life = dicom[0x0054, 0x0016][0][0x00181075].value
    total_dose = dicom[0x0054, 0x0016][0][0x00181074].value

    RP_sequence_tag = Tag(0x0054, 0x0016)
    RP_inner_tag = Tag(0x0018, 0x1078)

    if RP_sequence_tag in dicom:
        sequence = dicom[RP_sequence_tag]
        # VÃ©rifier si le tag interne existe dans le premier Ã©lÃ©ment de la sÃ©quence
        if RP_inner_tag in sequence[0]:
            radiopharmaceutical_start_date_time = sequence[0][RP_inner_tag].value

        else:
            radiopharmaceutical_start_date_time = 'Undefined'
    else:
        radiopharmaceutical_start_date_time = 'Undefined'

    if radiopharmaceutical_start_date_time == 'Undefined' or radiopharmaceutical_start_date_time == '':
        # If startDateTime not available use the deprecated statTime assuming
        # the injection is same day than acquisition date
        radiopharmaceutical_start_time = dicom[0x0054, 0x0016][0][0x0018, 0x1072].value
        radiopharmaceutical_start_date_time = acquisition_date + radiopharmaceutical_start_time

    radiopharmaceutical_start_date_time = parse_datetime(radiopharmaceutical_start_date_time)

    if (total_dose == 'Undefined' or total_dose is None or acquisition_datetime == 'Undefined'
            or patient_weight == 'Undefined' or patient_weight is None or \
            radionuclide_half_life == 'Undefined'):
        if logger is not None:
            logger.warning('Missing Radiopharmaceutical data or patient weight')
        print('Missing Radiopharmaceutical data or patient weight')

    # Determine Time reference of image acqusition
    acquisition_hour = series_datetime
    if (acquisition_datetime != 'Undefined'
            and (acquisition_datetime - series_datetime).total_seconds() < 0 and units == 'BQML'):
        acquisition_hour = acquisition_datetime
    if Tag(0x00541321) in dicom:
        decay_factor_ind= dicom[0x0054,0x1321].value
    else:
        decay_factor_ind = None

    # Calculate decay correction
    if decay_correction == 'START':
        delta = acquisition_hour - radiopharmaceutical_start_date_time
        delta = delta.total_seconds()
        if delta < 0:
            print('AcquisitionTimeException')
        if delta > 3600*24:
            logger.warning(f"Patient {patient_name}: Radiopharmaceutical Start time was more than a day before acquisition timee."
                          f"Setting delta = delta mod (1 day)")
            warnings.warn(f"Radiopharmaceutical Start time was more than a day before acquisition timee."
                          f"Setting delta = delta mod (1 day)")
            delta = delta%(3600*24)
        decay_factor = exp(-delta * log(2) / radionuclide_half_life)

    # If decay corrected from administration time no decay correction to apply
    elif decay_correction == 'ADMIN':
        decay_factor = 1


    else:
        logger.info('Unknown Decay Correction methode')
        print('Unknown Decay Correction methode')

    suv_conversion_factor = 1 / ((total_dose * decay_factor) / patient_weight)
    if units == 'CNTS':
        philips_suv_bqml = dicom[Tag(0x70531009)].value
        return philips_suv_bqml * suv_conversion_factor
    return suv_conversion_factor


def compute_suv(nifti, dicom, logger=None):
    """
        Computes the Standardized Uptake Value for the input image,
        using the metadata from the DICOM file
    """

    suv_factor = find_factor(dicom, logger)

    image_array = sitk.GetArrayFromImage(nifti)

    suv_image_array = image_array * suv_factor

    suv_image = sitk.GetImageFromArray(suv_image_array)

    suv_image.CopyInformation(nifti)

    return suv_image






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
                #series = os.listdir(join(root_dir, patient, modality, study))
                #for i, serie in enumerate(series):
                    #pass
                    try:
                        reader = sitk.ImageSeriesReader()
                        print(join(root_dir, patient, modality, study))
                        reader.SetFileNames(reader.GetGDCMSeriesFileNames(
                            join(root_dir, patient, modality, study)
                        ))
                        image = reader.Execute()
                        image_suv = compute_suv(image, pydicom.dcmread(os.listdir(join(root_dir, patient, modality, study))[0]))
                        sitk.WriteImage(image, join(root_dir, patient, modality, f"{study}.nii.gz"))
                    except:
                        print(f"{join(root_dir, patient, modality, study)} failed.")
    else:
        print(f"Found {num_studies} for patient {patient}.")

print(f"Patients OK PET/CT: {patients_petct}")
