# Organ-omics

## Organ radiomics extraction in python

This repository features the code needed to perform:
- automated organ segmentation (using [TotalSegmentator](https://github.com/wasserth/TotalSegmentator))
-  organ-omic (and radiomic) features extraction (using [pyRadiomics](https://github.com/AIM-Harvard/pyradiomics/))


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

If you only want to extract organomic features, labelsTs can be empty. It will be used to store organ contours once they are extracted. If you want to extract radiomic features of a lesion class, labelsTs can contain the lesions contours for each patient.

 

The file ```dataset.json``` should be constructed as shown in [this exemple](data/Dataset001_Test/dataset.json)

```json

{
    "name": "Test", // Dataset name
    "description": "Test 1", // Dataset description
    "channel_names": {
        // At least one channel named CT is needed for organ contouring
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
    // is defined in correspondance
    //
    // tasks is a list
    //
    // The task with most priority (i.e. the one who will erase 
    // labels from the others) should be the first element of the list
    // The priority order is defined by the position in the list
    "tasks":[
         {// First task
            // Task name (must be from TotalSegmentator)
            "name": "total",
            // Correspondance dictionnary
            "correspondance":
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
                "correspondance":{
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

### Extract organs contours

Using the following command in the root folder, organs contours will be saved in compressed NifTi (.nii.gz) files  in the `<contours_output_path>/labelsTr` folder.

```Organomics_contour_dataset -d <dataset_path> -o <contours_output_path>```

## Organomics extraction

Once the organ segmentation have ben extracted and are placed in the `labelsTr` folder, using the following command will compute the Organomics and place them in `<csv_file_organomics_output_path>/Organomics.csv`

``` Organomics_extract_organomics -d <dataset_path> -o <csv_file_organomics_output_path>```

## Radiomics extraction

To compare organomics and radiomics performance, wealso developped an automated radiomics extraction pipeline. To run this pipeline, you need a dataset structured as defined above, with lesion segmentatins placed in the labelsTs folder. Run it with the following command:

```python3 extract_radiomics -d <dataset_path> -o <csv_file_radiomics_output_path>```

## Results on the HECKTOR22 dataset

![Performance using Organomics for survival estimation](data/imgs/Organomics_performance.png)
Performance obtained using Organomics for survival estimation

![Performance using Radiomics for survival estimation](data/imgs/Radiomics_performance.png)
Performance obtained using Radiomics for survival estimation
