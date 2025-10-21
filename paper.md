---
title: 'Organ-omics: A Python package for organ-radiomics extraction'
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
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
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

In the early hours of personalized medicine, we present Organ-omics, an automated organ-radiomics extraction pipeline developed to be used with Python. Building on top of PyRadiomics for radiomics extraction and TotalSegmentator(TS) for automatic organ contouring, this tool extends the path to precision medicine.
Starting from a NifTi formatted dataset and a configuration file (JSON format), this tool allows an user to define a set of organs to be contoured using TotalSegmentator. Using the config file, the user can define organ groups, which can include multiple organs available in TS. All freely available TS tasks can be used and combined to create unique sets of organs. Some TS tasks require a license (see [here](https://backend.totalsegmentator.com/license-academic/)) which will need to be setup after TS is installed.
A spacing can also be defined in the config file, which will be used to resample images and masks before the features are computed.


# Statement of need

Radiomics are widely used in medical imaging studies. Lesions
They have some limitations:
- Uncertain, not very reproducible contours for VOIs such as lesions[ref interobserver]
- The limited amount of information available in a single area

Salimi et al. showed the importance surrounding tissue and organs can have for prognosis. 
They then showed how including organs as VOIs in a radiomic study improved the performance of ML algorithms when predicting Overall Survival (OS).  To name these organ-based radiomics they used the name organomics.

To the best of our knowledge, no automated organ-radiomics extraction pipeline is freely available to this day. Organ-omics looks to bridge this gap in software to facilitate and speedup extraction and as an effort to standardize organ radiomics extraction.

# Overview of Organ-omics
Our tool offers a complete pipeline from a dataset of medical images to organ radiomic features stored in a CSV file. Its only requirement is a specifc dataset format (see below). From a properly formatted dataset, it handles organ contours creation, using TS, then a second command handles the extraction of radiomic features from these contours. The extraction can be configured to resample the data to a common spacing to comply with the IBSI standard.

The NifTi file format is used through all the pipeline. This format allows us to keep the spatial informations while being quicker to process than DICOM. Once the organ groups contours are obtained they are stored as a multi-class mask, same dimensions as the CT volume, in a NifTi file.

## Technical overview

### Key Features
 - **User-defined configuration**: Parse a user-defined configuration from a json file. Labels to extract and organ groups are defined in this file.
 - **Adaptative organ contours extraction**: Using the user-defined configuration, TS is used on the CT images efficiently (i.e.: when possible, the *roi_subset* parameter is defined to limit runtime). Still using this configuration, organs are gathered in groups and the final organ groups multi-label map is generated.
 - **Radiomic features extraction**: 107 features per Region Of Interest (ROI) are extracted using the PyRadiomics library. Additional info is pulled from the configuration file to comply with the IBSI standard:
   -  *Isotropic spacing*: it is possible not to define it, or to use an anisotropic spacing. However a warning will be issued since this breaks IBSI compliance
  These features are stored in a CSV file with *n_cases* rows and  *n_features* columns.


### Applications and Limitations
#### Pre-requisite

The only pre-requisite to use this tool is using the nnUNet format:
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
    
Organ-omics enables the exploration by clinicians and other researchersof the healthy organs' impact on patient survival and treatment response. It moves us one step closer to a completely automated analysis, from patient imaging to treatment personalization.

To get the most from Organ-omics, the Field Of View (FOV) during acquisition should be:
 - As broad as possible: to include the most organs
 - The same for all patients: if an organ is cropped in a patient's scan, the radiomic features might be incorrect (e.g.: Volume, Sphericity, Maximum). If an organ is completely out of FOV, missing values will be introduced, which will impact the performance of downstream tasks.



# Real-World Example
![Organs from 2 tasks: total and abdominal_muscles](images/Mixed_tasks_organ_contours.png)
**Figure 1**: This picture shows organs from two TS tasks: *heart*, *lung*(all lung lobes) and *thoracic vertebrae*(T1-T12) from the **total** task; *pectoralis major* (right and left grouped) and *rectus abdominis* (also right/left) from the task **abdominal_muscles**. This result is available to reproduce in [the examples](examples/paper_example.sh).