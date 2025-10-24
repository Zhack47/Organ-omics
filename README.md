# Organ-omics

## Organ radiomics extraction using Python
Organ-omics is intended to accelerate research on organ-based radiomics and to improve reproducibility across such studies.
Organ-omics lets you automatically create organ contours using [TotalSegmentator](https://github.com/wasserth/TotalSegmentator). It then extracts radiomic features using [PyRadiomics](https://github.com/AIM-Harvard/pyradiomics/) from these contours across a whole dataset. Its contouring pipeline allows you to create custom organ sets with no additional code through a JSON config file. Organ-omics can be used as an end-to-end pipeline and is modular, using NIfTi files each step of the way, allowing you to use either the organ contouring or the radiomic extraction part on their own.

## Installation

### Install PyRadiomis from GitHub

We recommend installing PyRadiomics (required depndency) using the GitHub main branch since the PyPi distribution seems broken (see [this issue](https://github.com/AIM-Harvard/pyradiomics/issues/900))

`pip install git+https://github.com/AIM-Harvard/pyradiomics.git`

### Organ-omics from Test PyPI

⚠️ Organ-omics is currently available via Test PyPI

`pip install -i https://test.pypi.org/simple/ organomics`

You can also install it from source

```
git clone https://github.com/Zhack47/Organ-omics.git
cd organomics
pip install -e .
```

## Data format

Your data should be organized following the nnUNet dataset format:

```bash
dataset_path
  ├── dataset.json
  └── imagesTr/
     ├── P001_0000.nii.gz
     ├── P001_0001.nii.gz
     ├── P002_0000.nii.gz
     ├── P002_0001.nii.gz
     ├── ...
  └── labelsTr/ 
      ├── 
```

The `labelsTr` folder can be empty as it will be used to store organ contours once they are extracted. If you want to extract radiomic features of an already contoured lesion class, labelsTr can contain the lesions contours for each patient.

 

The file `dataset.json` should be constructed as shown in [this example](https://raw.githubusercontent.com/Zhack47/Organ-omics/refs/heads/main/data/Dataset001_Test/dataset.json)

```json

{
    "name": "Test", // Dataset name
    "description": "Test 1", // Dataset description
    "channel_names": {
        // Needs at least one channel named CT for organ contouring
        "0": "CT", 
        "1": "PT"
    },
    // Target isotropic spacing for resampling
    "spacing": [2,2,2],
    
    // List of organ groups
    "labels":
    {
        "background": "0",
        "heart": "1",
        "lungs": "2",
        "thoracic vertebrae": "3",
        "pectoralis": "4",
        "rectus": "5"
    },
    // For each task, the name of the task is defined
    // then the mapping from task organs to organ groups
    // is defined in correspondence

    // The priority order (i.e. which task will overwrite the labels 
    // the others) is defined by the position in the list
    "tasks":[
         {// First task
            // Task name (must be from TotalSegmentator)
            "name": "total",
            // Correspondence dictionnary
            "correspondence":
                {
                    "heart": ["heart"],
                    "lungs": [
                     "lung_upper_lobe_left", "lung_lower_lobe_left",
                     "lung_upper_lobe_right","lung_middle_lobe_right",
                      "lung_lower_lobe_right"],
                    "thoracic vertebrae": [
                     "vertebrae_T1", "vertebrae_T2", "vertebrae_T3",
                     "vertebrae_T4", "vertebrae_T5", "vertebrae_T6",
                     "vertebrae_T7", "vertebrae_T8", "vertebrae_T9",
                     "vertebrae_T10","vertebrae_T11","vertebrae_T12"
                     ]
                }
            },
            {// Second task
                "name": "abdominal_muscles", 
                "correspondence":{
                    "pectoralis": [
                     "pectoralis_major_right", "pectoralis_major_left"
                     ],

                    "rectus": [
                     "rectus_abdominis_right", "rectus_abdominis_left"
                    ]
                }
            }
        ]
}

```

**Multiple tasks from TotalSegmentator can be combined** to create custom organ sets.

⚠️ Some tasks can only be used with a license issued by the team maintaining TotalSegmentator. **No license can be obtained through Organ-omics**

## Organs contours extraction

Using the following command in the root folder, organs contours will be saved in compressed NIfTi (.nii.gz) files  in the `<contours_output_path>/labelsTr` folder.

```Organomics_contour_dataset -d <dataset_path> -o <contours_output_path>```

## Organ radiomics extraction

Once the organ contours have been extracted and stored in the `labelsTr` folder of the dataset, use the following command to compute the organ radiomics.

``` Organomics_extract_radiomics -d <dataset_path> -o <csv_file_organomics_output_path>```

Radiomic feature values will be stored in the file defined with the `-o` option.



[//]: <> (## Results on the HECKTOR22 dataset)

[//]: <> (![Performance using Organ-omics for survival estimation]data/imgs/Organomics_performance.png)
[//]: <> (Performance obtained using Organ-omics for survival estimation)

[//]: <> (![Performance using Radiomics for survival estimation]data/imgs/Radiomics_performance.png)
Performance obtained using Radiomics for survival estimation)


# Citation

If you use Organ-omics in your research, please cite:

```
Zacharia Mesbah (2025). Organ-omics: A Python package for organ-radiomics extraction.
```

# References

Wasserthal, J., Breit, H.-C., Meyer, M.T., Pradella, M., Hinck, D., Sauter, A.W., Heye, T., Boll, D., Cyriac, J., Yang, S., Bach, M., Segeroth, M., 2023. TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images. Radiology: Artificial Intelligence. https://doi.org/10.1148/ryai.230024

van Griethuysen, J. J. M., Fedorov, A., Parmar, C., Hosny, A., Aucoin, N., Narayan, V., Beets-Tan, R. G. H., Fillion-Robin, J. C., Pieper, S., Aerts, H. J. W. L. (2017). Computational Radiomics System to Decode the Radiographic Phenotype. Cancer Research, 77(21), e104–e107. https://doi.org/10.1158/0008-5472.CAN-17-0339