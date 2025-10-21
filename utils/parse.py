""" Module for JSON files parsing and nnUNet-format dataset handling"""
import os
import json
import warnings
from os.path import join
import numpy as np


def load_cases(root_path, json_filepath):
    """ Load names and images/labels paths from a nnUNet formated dataset.
    Also parses the JSON configuration files and checks for inconsistencies

    Args:
        root_path (str): root of the nnUNet dataset
        json_filepath (str): path of the JSON configuration file
    
    Returns: 
        list_images: list of all image file paths
        list_labels: list of all label file paths
        list_cases: list of all identified cases
        channels: dictionary of the available channels per case
        nb_channels: number of channels
        channel_ct: number of the channel which corresponds to the CT (to be used as input for TotalSegmentator)
        classes: list of classes (organ groups names)
        spacing: User defined common isotropic spacing. Can be None if not specified in the configuration file
    """
    with open(join(root_path, json_filepath), "rb") as json_file:
        dataset_json = json.load(json_file)
    # Get spacing for resampling
    try:
        spacing = dataset_json["spacing"]
        if len(spacing) != 3:
            spacing = None
            raise ValueError("Wrong spacing format!")
        if len(set(spacing))!=1:
            warnings.warn("Anisotropic spacing detected! This breaks the IBSI standard.")
    except (KeyError, ValueError) as e:  # This part is ugly, but who knows wht error can be triggered through user input...
        if isinstance(e, ValueError) and str(e) != "Wrong spacing format!":
            raise e
        spacing = None
        warnings.warn("No common isotropic spacing was defined! This breaks the IBSI standard.")

    
    channels = dataset_json["channel_names"]
    nb_channels = len(channels.keys())
    channel_ct = np.argwhere(np.array(list(dataset_json["channel_names"].values()))=="CT").squeeze()
    images_root_path = join(root_path, "imagesTr")
    labels_root_path = join(root_path, "labelsTr")

    list_images = os.listdir(images_root_path)
    list_labels = os.listdir(labels_root_path)

    # Only check for consistency if labels are present.
    # We want to be able to handle the case where no labels are present
    # e.g. before organs are contoured using TotalSeg
    if len(list_labels):
        good_nb_images = nb_channels*len(list_labels)
        assert len(list_images) == good_nb_images, f"Found {len(list_labels)} labels,\
                                                                 should be {good_nb_images} images\
                                                                 but found {len(list_images)}"
    # Get case names from image names, removing the trailing _XXXX.nii.gz (nnUNet format)
    list_cases = list(set([i.split(".nii.gz")[0][:-5] for i in list_images]))
    classes = dataset_json["labels"]
    return list_images, list_labels, list_cases, channels, nb_channels, channel_ct, classes, spacing


def config_total_seg(dastaset_json_path):
    """Extracts the configuration from a .json file.

    Args:
        dastaset_json_path (str): Path to the dataset.json file

    Returns:
        list, dict, dict: List of organs, organ groups and their label number, organ groups
          and the corresponding organs 
    """
    with open(dastaset_json_path, "rb") as json_file:
        json_object = json.load(json_file)

    tasknames = []
    organs_to_extract = []
    new_correspondance = {}
    tasks: list = json_object["tasks"]
    labels_dict = json_object["labels"]
    for task in tasks:
        task_name = task["name"]
        new_correspondance[task_name] = {}
        tasknames.append(task_name)
        correspondance = task["correspondance"]
        for group, labels_list in correspondance.items():
            if group in labels_list:
                if group not in new_correspondance:
                    new_correspondance[task_name][group] = []
                for single_label in labels_list:
                    new_correspondance[task_name][group].append(single_label)
                    organs_to_extract.append(single_label)
    return organs_to_extract, labels_dict, new_correspondance


    ##########
    task = json_object["task"]
    labels_dict = json_object["labels"]
    label_groups = list(labels_dict.keys())
    correspondance = json_object["correspondance"]

    for label_group in label_groups[1:]:  # 0 should be background (for compatibility with nnunet format)
        for label in correspondance[label_group]:
            organs_to_extract.append(label)
    return organs_to_extract, labels_dict, correspondance, tasknames

def display_radiomics_config(names, channels, classes, spacing):
    """Displays a summary of the configuration which will be used
      to extract radiomic features.

    Args:
        names (_type_): List of the patient names present in the dataset
        channels (_type_): List of channels (imaging modalities), available for each patient
        classes (_type_): List of segmentation classes (ROIs)
        spacing (_type_): Target common spacing. Can be None if no spacing
          has been specified, but this breaks IBSI copliance
    """
    res = f"We found {len(names)} patients, with {len(channels)} channels each.\n"
    res += f"The segmentation classes are {classes}\n"
    if spacing is None:
        res+= "No spacing was provided for rsampling, keeping original spacing (Warning: this breaks ISI standard)\n"
    else:
        res+=f"Volumes will be resampled to a {spacing} spacing.\n"
    print(res)


if __name__ == "__main__":
    images_, labels_, names_, channels_, nb_channels_, channel_ct_, classes_, spacing_ = load_cases("../data/Dataset001_Test")
