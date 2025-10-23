---
title: 'Organ-omics: A Python package for automated organ-radiomics extraction'
tags:
  - Python
  - medical imaging
  - radiomics
  - organs
  - CT scan
authors:
  - name: Zacharia MESBAH
    orcid: 0009-0008-4604-6852
    equal-contrib: true
    affiliation: "1,2" # (Multiple affiliations must be quoted)
affiliations:
 - name: AIMS-QuantIF, Rouen Normandy University, France
   index: 1
 - name: Siemens Healthcare SAS
   index: 2
date: \today
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
#aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
#aas-journal: Astrophysical Journal <- The name of the AAS journal.
---
# Summary

To support personalized medicine, we present Organ-omics, an automated organ-radiomics extraction pipeline developed to be used with Python. Building on top of PyRadiomics [@van2017computational] for radiomics extraction and TotalSegmentator [@wasserthal2023totalsegmentator] for automatic organ contouring, this tool extends the path to precision medicine.
Starting from a NifTi formatted dataset and a configuration file (JSON format), this tool allows a user to define a set of organs to be contoured using TotalSegmentator (TS). Using the config file, the user can define organ groups, which can include multiple organs available in TS. All freely available TS tasks can be used and combined to create unique sets of organs. Some TS tasks require a license (see [here](https://backend.totalsegmentator.com/license-academic/)) which must be set up after TS is installed.
A spacing can also be defined in the config file, which will be used to resample images and masks before the features are computed.


# Statement of need

Radiomics derived from lesions are widely used in medical imaging studies, but lesion-based approaches have limitations: contouring is uncertain, not reproducible [@podobnik2024voariability] and a limited amount of information is provided using this method.

Prior work [@salimi2024organomics] has shown that surrounding tissue and organs carry a signal that is important for patient prognosis and that including organ-based radiomic features can improve the predictive performance of ML algorithms for outcomes such as Overall Survival (OS). To name these organ-based radiomics they used the name organomics.

To our knowledge, there is no freely available end-to-end pipeline that automates organ-based radiomics extraction from medical imaging datasets. Organ-omics fills this gap by providing an automated and configurable Python pipeline which (1) generates organ contours using TS (2) groups organs according to a user-defined configuration and (3) extracts reproducible organ-level radiomic features using PyRadiomics.

Organ-omics is intended to accelerate research on organ-based radiomics and to improve reproducibility across studies.

# Overview of Organ-omics
Organ-omics is a command line Python package which extracts a CSV table of organ-level radiomic features. A user provides a JSON configuration file (see below) that specifies which segmentation tasks from TS should be used and how labels should be grouped to form the final labels: organ groups. 

The pipeline then runs TS efficiently by limiting the organs to the necessary minimum (through roi_subset, when available) and assembles labels according to the configuration.

**Command:** `organomics_contour_dataset -d [path_to_dataset] -o [path_to_labels_output] --json-file [path_to_JSON_file]`

A second step computes the 107 organ-level radiomic features for each organ group using PyRadiomics and stores them in a single CSV file.

This radiomics extraction can be configured to resample the data to a common isotropic spacing to comply with the IBSI standard [@hatt2018ibsi].



**Command:** `organomics_extract_organomics -d [path_to_dataset] -o [path_to_csv_output] --json-file [path_to_JSON_file]`

Organ-omics uses NIfTi at every step and can be integrated into larger preprocessing workflows or used as a standalone tool for organ radiomics studies.

## Technical overview

### Key Features
  - **User-defined configuration**: parsing a user-defined JSON configuration file Organ-omics extracts:
    - **Input channels**: one should be named *'CT'* and is used for organ contouring using TS, the remaining ones are stored for radiomics extraction since a set of organ radiomics is extracted per modality. 
  
    -  **Final labels**: names of all the organ groups (+ background which must be 0)

    - **TotalSegmentator tasks**: each one is defined by its name and includes a dictionary indicating how organs should be grouped.

    - **Spacing**: To respect IBSI recommendations, this should be an isotropics spacing. If it is defined, images and masks will be resampled towards this spacing before radiomics are computed, applying third order BSpline interpolation to images and nearest neighbour interpolation to masks.

 - **Adaptive organ contours extraction**: Using the user-defined configuration, TS is used on the CT images efficiently (i.e.: when possible, the *roi_subset* parameter is defined to limit runtime).
 
   Organs are gathered in groups according to the user configuration and each organ group can contain one or more organs from a task. A set of organ group is defined for each task, but only organs from the same task can be included in the same group.

   **The priority for labels follows the order of the *tasks* list.** If a label for an organ-group defined in the task at index 1 in the list is overlapping with a label originating from the task at index 0, the label from the task at index 0 will be kept.

 - **Radiomic features extraction**: 107 radiomic features per Region Of Interest (ROI) are extracted using the PyRadiomics library.
 
   These features are stored in a CSV file as defined above.


### Pre-requisite

A pre-requisite to Organ-omics is a specific dataset format [@isensee2021nnu]:

 - All images must be in **NifTi file format**

 - The following **dataset structure** must be respected:
  
  
```
|-root_folder
    |-imagesTr
      |-P01_0000.nii.gz
      |-P01_0001.nii.gz
      |-...
    |-labelsTr

```

### Limitations

To get the most from Organ-omics, the Field Of View (FOV) during acquisition should be:
 - As broad as possible: to include the most organs
 - The same for all patients: if an organ is cropped in a patient's scan, the radiomic features might be incorrect (e.g.: Volume, Sphericity, Maximum). If an organ is completely out of FOV, missing values will be introduced, which will impact the performance of downstream tasks.

### Applications

Organ-omics enables the exploration by clinicians and other researchers of the healthy organs' impact on patient survival and treatment response. It moves us one step closer to a completely automated analysis, from patient imaging to treatment personalization.


# Real-World Example

![Organs from 2 tasks: total and abdominal_muscles](./images/Mixed_tasks_organ_contours.png)

This picture shows organ groups from two TS tasks:

- **heart** (only the heart), **lung**(all lung lobes) and **thoracic vertebrae**(T1-T12) from **total**

- **pectoralis major** (right/left) and **rectus abdominis** (right/left) from **abdominal_muscles**.

This result can be reproduced using [a script available on the repository](https://github.com/Zhack47/Organ-omics/blob/main/examples/paper_example.sh).

# References