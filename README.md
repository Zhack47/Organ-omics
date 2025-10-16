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
      ├── P001.nii.gz
      ├── P002.nii.gz
      ├── ...
```

If you only want to extract organomic features, labelsTs can be empty. It will be used to store organ contours once they are extracted. If you want to extract radiomic features of a lesion class, labelsTs should contain the contours of these lesions for each patient.

The file ```dataset.json``` should be constructed as shown in [this exemple](data/Dataset001_Test/dataset.json)

### Extract organs contours

Using the following command in the root folder, organs contours will be saved in compressed NifTi (.nii.gz) files  in the `<contours_output_path>/labelsTr` folder.

```python3 contour_dataset -d <dataset_path> -o <contours_output_path>```

## Organomics extraction

Once the organ segmentation have ben extracted and are placed in the `labelsTr` folder, using the following command will compute the Organomics and place them in `<csv_file_organomics_output_path>/Organomics.csv`

```python3 extract_organomics -d <dataset_path> -o <csv_file_organomics_output_path>```

## Radiomics extraction

To compare organomics and radiomics performance, wealso developped an automated radiomics extraction pipeline. To run this pipeline, you need a dataset structured as defined above, with lesion segmentatins placed in the labelsTs folder. Run it with the following command:

```python3 extract_radiomics -d <dataset_path> -o <csv_file_radiomics_output_path>```

## Results on the HECKTOR22 dataset

![Performance using Organomics for survival estimation](data/imgs/Organomics_performance.png)
Performance obtained using Organomics for survival estimation

![Performance using Radiomics for survival estimation](data/imgs/Radiomics_performance.png)
Performance obtained using Radiomics for survival estimation
