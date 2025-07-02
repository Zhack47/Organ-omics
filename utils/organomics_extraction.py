import os
from os.path import join
from utils.parse import load_names
from utils.volumes.masks import load_mask, resample_mask
from utils.volumes.images import load_image
from utils.radiomics.extraction import Radiomics_Extractor
from tqdm import tqdm


def extract_organomics(root_dataset_path, output_directory):
    """Extracts organ radiomics for a whole nnUNet dataset

    Args:
        root_dataset_path (str): path to the root of the nnUNet dataset
        output_directory (str): Output directory where the csv file will be saved TODO define naming convention
    """
    _, _, names, channels, _, _, classes = load_names(root_dataset_path)
    del classes["background"]  # Remove the background from channels
    os.makedirs(output_directory, exist_ok=True)
    out_csv_file = open(join(output_directory, "bla.csv"), "w", encoding="utf-8")


    # Write columns headers
    out_csv_file.write("Patient_ID")
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
            for class_name, mask in masks.items():
                print(class_name)                    
                re = Radiomics_Extractor(image, mask)
                feature_vector = re.get_feature_vector()
                for key, _ in feature_vector.items():
                    out_csv_file.write(f",{modality_name}_{class_name}_{key}")
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
            for class_name, mask in masks.items():
                re = Radiomics_Extractor(image, mask)
                feature_vector = re.get_feature_vector()
                for _, value in feature_vector.items():
                    out_csv_file.write(f",{value}")
        out_csv_file.write("\n")

    out_csv_file.close()
