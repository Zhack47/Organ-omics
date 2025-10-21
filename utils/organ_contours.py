"""
Module for automatic organ segmentation using TotalSegmentator
"""
import os
import numpy as np
from os.path import join

import nibabel as nib
from totalsegmentator.python_api import totalsegmentator, class_map

from utils.parse import config_total_seg, load_cases


def segment_group_save(dastaset_json_path, ct_path, output_fpath, **total_seg_kwargs):
    """Segments the CT then groups the organs according to the dataset.json config. Saves
    one segmentation .nii.gz (nifti) file in output_fpath.

    Args:
        dastaset_json_path (str): Path to the dataset.json file
        ct_path (str): Path to the CT scan
        output_fpath (str): Path to the file where the output is saved
        total_seg_kwargs (dict): TotalSegmentator additional arguments
    """
    
    # Extracting configuration from the dataset.json file
    roi_subsets, labels, labels_map = config_total_seg(dastaset_json_path)
    tasks = labels_map.keys()
    for task in tasks:
        if task not in ["total", "total_mr"]:  # roi_subset option is only available for the total and total_mr models
            roi_subset = None
        else:
            roi_subset = roi_subsets[task]

        # Performing organs segmentation and returning a nifti object (not saved as a file)
        print(task, roi_subset, total_seg_kwargs)
        nii_seg = totalsegmentator(nib.load(ct_path), task=task, roi_subset=roi_subset,
                                skip_saving=True, **total_seg_kwargs)
        affine = nii_seg.affine
        data = np.array(nii_seg.dataobj)
        try:
            out
        except NameError:
            out = np.zeros_like(data)
        # Grouping organs as defined in dataset.json
        grouped_data = np.zeros_like(data)
        reverse_map = {v: k for k, v in class_map[task].items()}
        for group_label in list(labels_map[task].keys())[1:]:
            for roi in labels_map[task][group_label]:
                label = reverse_map[roi]
                grouped_data[data==label]=int(labels[group_label])
        print(out.shape, grouped_data.shape)
        out = np.where(out[grouped_data>0], grouped_data, out)
        print(out.shape)
    new_nib_image = nib.Nifti1Image(grouped_data, affine=affine)
    nib.save(new_nib_image, output_fpath)


def segment_dataset(root_dataset_path, output_directory, dataset_json_filename):
    """Performs organ segmentation for a whole nnUNet dataset

    Args:
        root_dataset_path (str): Path for the root of the dataset
        output_directory (str): Directory in which the organ segmentation will be stored
    """
    _, _, names, _, _, ct_channel, _, _ = load_cases(root_dataset_path,
                                                     dataset_json_filename)
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(join(output_directory, "labelsTr"), exist_ok=True)
    for name in names:
        image_path = f"{name}_{str(ct_channel).zfill(4)}.nii.gz"
        segment_group_save(join(root_dataset_path, dataset_json_filename),
                           join(root_dataset_path, "imagesTr", image_path),
                           join(output_directory,"labelsTr", f"{name}.nii.gz"))


if __name__ == "__main__":
    segment_dataset("../data/Dataset001_Test", "../data/organs_Test")
