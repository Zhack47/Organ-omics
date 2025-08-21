""" Module for JSON files parsing and nnUNet-format dataset handling"""
import os
import json
from os.path import join
import numpy as np


def load_names(root_path):
    """ Load names and images/labels paths from a nnUNet formatted dataset

    Args:
        root_path (str): root of the nnUNet dataset
    """
    with open(join(root_path, "dataset.json"), "rb") as json_file:
        dataset_json = json.load(json_file)
    
    channels = dataset_json["channel_names"]
    spacing = dataset_json["spacing"]
    nb_channels = len(channels.keys())
    channel_ct = np.argwhere(np.array(list(dataset_json["channel_names"].values()))=="CT").squeeze()
    images_root_path = join(root_path, "imagesTr")
    labels_root_path = join(root_path, "labelsTr")

    list_images = os.listdir(images_root_path)
    list_labels = os.listdir(labels_root_path)
    good_nb_images = nb_channels*len(list_labels)
    """assert len(list_images) == nb_channels * len(list_labels), f"Found {len(list_labels)} labels,\
                                                                 should be {good_nb_images} images\
                                                                 but found {len(list_images)}"
    """
    list_names = list(set([i.split(".nii.gz")[0][:-5] for i in list_images]))
    classes = dataset_json["labels"]
    return list_images, list_labels, list_names, channels, nb_channels, channel_ct, classes, spacing


def config_total_seg(dastaset_json_path):
    """Extracts the configuration from a .json file.

    Args:
        dastaset_json_path (str): Path to the dataset.json file

    Returns:
        list, dict, dict: List of organs, organ groups and their label number, organ groups and the corresponding organs 
    """
    with open(dastaset_json_path, "rb") as json_file:
        json_object = json.load(json_file)

    task = json_object["task"]
    labels_dict = json_object["labels"]
    label_groups = list(labels_dict.keys())
    correspondance = json_object["correspondance"]

    organs_to_extract = []
    for label_group in label_groups[1:]:  # 0 should be background (for compatibility with nnunet format)
        for label in correspondance[label_group]:
            organs_to_extract.append(label)
    return organs_to_extract, labels_dict, correspondance, task


if __name__ == "__main__":
    images, labels, names, ct_channel = load_names("../data/Dataset001_Test")
