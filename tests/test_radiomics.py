import sys
import pytest
import SimpleITK as sitk
sys.path.append("../organomics")
from utils.radiomics_extraction import resample_image_to_spacing
from utils.parse import load_cases


class TestRadiomics:
    image = sitk.ReadImage("data/Dataset001_Test/imagesTr/CT_Abdo_001_0000.nii.gz")
    def test_spacing_int(self):
        _,_,_,_,_,_,_,spacing = load_cases("data/Dataset001_Test", "data/sample_configs/dataset_int_spacing.json")
        resample_image_to_spacing(self.image, spacing=spacing)
    
    def test_spacing_float(self):
        _,_,_,_,_,_,_,spacing = load_cases("data/Dataset001_Test", "data/sample_configs/dataset_float_spacing.json")        
        resample_image_to_spacing(self.image, spacing=spacing)

    def test_wrong_length(self):
        with pytest.raises(ValueError):
            load_cases("data/Dataset001_Test", "data/sample_configs/dataset_wrong_spacing.json")
    
    def test_no_spacing(self):
        with pytest.warns(match="No common isotropic spacing was defined! This breaks the IBSI standard."):
            load_cases("data/Dataset001_Test", "data/sample_configs/dataset_no_spacing.json")
    
    def test_anisotropic_spacing(self):
        with pytest.warns(match="Anisotropic spacing detected! This breaks the IBSI standard."):
            load_cases("data/Dataset001_Test", "data/sample_configs/dataset_anisotropic_spacing.json")