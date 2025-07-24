# Organ-omics
## Organ radiomics extraction in python

This repository features the code needed to perform automated organ segmentation (using TotalSegmentator) and organ radiomic features extraction (using pyRadiomics).

## Organs segmentation

The dataset must be in the nnUNet format:

```bash
dataset_path
  ├── dataset.json
  └── imagesTr/
     ├── P001_0000.nii.gz
     ├── P001_0001.nii.gz
     ├── P002_0000.nii.gz
     ├── P002_0001.nii.gz
     ├── ...
  └── labelsTr/  # This will be the folder containing organ contours once they are extracted
      ├── P001.nii.gz
      ├── P002.nii.gz
      ├── ...
```

```dataset.json``` should be constructed as shown in [this exemple](data/Dataset001_Test/dataset.json)

### Extract organs contours

Using the following command in the root folder, organs contours will be saved in compressed NifTi (.nii.gz) files  in the `<contours_output_path>/labelsTr` folder.

```python3 contour_dataset -d <dataset_path> -o <contours_output_path>```

## Organomics extraction

Once the organ segmentation have ben extracted and are placed in the `labelsTr` folder, using the following command will compute the Organomics and place them in `<csv_file_organomics_output_path>/Organomics.csv`

```python3 extract_organomics -d <dataset_path> -o <csv_file_organomics_output_path>```

