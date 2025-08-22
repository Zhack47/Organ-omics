import os
from os.path import join
from tqdm import tqdm
import SimpleITK as sitk
import numpy as np

from utils.parse import load_names
from utils.volumes.images import load_image, resample_image_to_spacing
from utils.radiomics.extraction import Radiomics_Extractor
from utils.volumes.masks import load_mask, resample_mask, bb_sitk


def crop_image_mask(image: sitk.Image, mask: sitk.Image, margin=(0, 0, 0)):
    """Crops both the input mask and image to the bouding box of the nonzero values in the mask. 
        A margin can be defined (default: 0 on all sides)to increase the bouning box.
        However the margin cannot exceed the original size, in any direction.
        If it does, the image border is kept as such in this direction.
    Args:
        image (SimpleITK.Image): _description_
        mask (SimpleITK.Image): _description_
        margin (tuple, optional): _description_. Defaults to (0, 0, 0).

    Returns:
        (tuple): A tuple containing the cropped image and the cropped mask.
    """
    X, Y, Z = mask.GetSize()
    start_index_x, start_index_y, start_index_z, size_x, size_y, size_z =bb_sitk(mask)
    start =  [max(0, start_index_x - margin[2]), max(0, start_index_y - margin[1]), max(0, start_index_z - margin[0])]
    size =  [min(X-start_index_x, size_x + margin[2]), min(Y - start_index_y, size_y     + margin[1]),
             min(Z-start_index_z, size_z + margin[0])]
    cropped_image = sitk.RegionOfInterest(image, size, start)
    cropped_mask = sitk.RegionOfInterest(mask, size, start)
    return cropped_image, cropped_mask

def extract_organomics(root_dataset_path, output_directory):
    """Extracts organ radiomics for a whole nnUNet dataset

    Args:
        root_dataset_path (str): path to the root of the nnUNet dataset
        output_directory (str): Output directory where the Organomics.csv file will be saved
    """
    _, _, names, channels, _, _, classes, spacing = load_names(root_dataset_path)
    del classes["background"]  # Remove the background from channels
    os.makedirs(output_directory, exist_ok=True)
    out_csv_file = open(join(output_directory, "Organomics.csv"), "w", encoding="utf-8")


    # We do a first blank pass in order to write the columns' names
    # Maybe we could do thiss diifferently?
    out_csv_file.write("Patient_ID")
    feature_names = set()
    for name in names[:1]:
        # Extracting all masks once
        masks = {}
        label_path = join(root_dataset_path, "labelsTr", f"{name}.nii.gz")
        for class_name, class_label in classes.items():
            label = load_mask(label_path,label=int(class_label))
            masks[class_name] = label
        for modality_value, modality_name in channels.items():
            image_path = join(root_dataset_path, "imagesTr", f"{name}_{str(modality_value).zfill(4)}.nii.gz")
            image = load_image(image_path)
            image = resample_image_to_spacing(image, spacing)
            for class_name, mask in masks.items():
                mask = resample_mask(mask, image)
                cropped_image, cropped_mask = crop_image_mask(image, mask, margin=(2,2,2))
                re = Radiomics_Extractor(cropped_image, cropped_mask)
                feature_vector = re.get_feature_vector()
                for key, _ in feature_vector.items():
                    out_csv_file.write(f",{modality_name}_{class_name}_{key}")
                    feature_names.add(key)
        out_csv_file.write("\n")

    for name in tqdm(names):
        out_csv_file.write(name)
        # Extracting all masks once
        masks={}
        label_path = join(root_dataset_path, "labelsTr", f"{name}.nii.gz")
        for class_name, class_label in classes.items():
            label = load_mask(label_path,label=int(class_label))
            masks[class_name] = label

        for modality_value, _ in channels.items():
            suffix = str(modality_value).zfill(4)
            image_path = join(root_dataset_path, "imagesTr", f"{name}_{suffix}.nii.gz")
            image = load_image(image_path)
            if spacing is not None:
                image = resample_image_to_spacing(image, spacing)
            for class_name, mask in masks.items():
                mask = resample_mask(mask, image)
                mask_array = sitk.GetArrayFromImage(mask)
                first_value = mask_array.flat[0]
                if  not np.all(mask_array==first_value) and np.sum(mask_array)>1:  # TODO replace with GetSum or sth from SimpleITK
                    cropped_image, cropped_mask = crop_image_mask(image, mask, margin=(2,2,2))
                    re = Radiomics_Extractor(cropped_image, cropped_mask)
                    feature_vector = re.get_feature_vector()
                    for _, value in feature_vector.items():
                        out_csv_file.write(f",{value}")
                else:
                    for _ in feature_names:
                        out_csv_file.write(f",{np.nan}")
        out_csv_file.write("\n")

    out_csv_file.close()
