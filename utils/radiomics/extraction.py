import sys
import copy
import numpy as np
import logging
import inspect
import SimpleITK as sitk
from radiomics.shape import RadiomicsShape
from radiomics.firstorder import RadiomicsFirstOrder
from radiomics.glcm import RadiomicsGLCM
from radiomics.glszm import RadiomicsGLSZM
from radiomics.glrlm import RadiomicsGLRLM
from radiomics.ngtdm import RadiomicsNGTDM
from radiomics.gldm import RadiomicsGLDM
sys.path.append("../../")
from utils.volumes.images import load_image  # , resample_image
from utils.volumes.masks import load_mask, bb_sitk, resample_mask, apply_numpy_fn, add_pos


AVAILABLE_EXTRACTORS = {"Shape": RadiomicsShape, "FirstOrder": RadiomicsFirstOrder, "GLCM": RadiomicsGLCM,
                        "GLSZM": RadiomicsGLSZM, "GLRLM": RadiomicsGLRLM, "NGTDM": RadiomicsNGTDM, "GLDM": RadiomicsGLDM}
is_feat_method = lambda x: inspect.ismethod(x)

logger = logging.getLogger(__name__)


def crop_image_mask(image: sitk.Image, mask: sitk.Image, margin=(0, 0, 0)):
    X, Y, Z = mask.GetSize()
    start_index_x, start_index_y, start_index_z, size_x, size_y, size_z =bb_sitk(mask)
    start =  [max(0, start_index_x - margin[2]), max(0, start_index_y - margin[1]), max(0, start_index_z - margin[0])]
    size =  [min(X-start_index_x, size_x + margin[2]), min(Y - start_index_y, size_y     + margin[1]),
             min(Z-start_index_z, size_z + margin[0])]
    cropped_image = sitk.RegionOfInterest(image, size, start)
    cropped_mask = sitk.RegionOfInterest(mask, size, start)
    return cropped_image, cropped_mask

class Radiomics_Extractor:
    def __init__(self, image, mask):
        self.mask_is_empty = False
        # Resampling the mask towards the image's space is faster (NearestNeighbor instead of BSpline..)
        # This code is kept there if we need to do the opposite, idk why we would but anyway..
        # image = resample_image(image, to=mask)
        mask_array = sitk.GetArrayFromImage(mask)
        first_value = mask_array.flat[0]
        # If there is only one voxel, GLCM can't work
        if not np.all(mask_array==first_value) and np.sum(mask_array)>1:
            mask = resample_mask(mask, to=image)
            image, mask = crop_image_mask(image, mask)
            self.extractors = {extractor_name: AVAILABLE_EXTRACTORS[extractor_name](image, mask)
                                for extractor_name in AVAILABLE_EXTRACTORS}
            # Suppressing the annoying symmetrical glcm warning
            if "GLCM" in self.extractors.keys():
                self.extractors["GLCM"].logger.setLevel(logging.ERROR)
            for extractor_name in self.extractors:
                logger.debug(f"Initializing calculations for {extractor_name}... ")
                try:
                    self.extractors[extractor_name]._initCalculation()
                except Exception:
                    self.mask_is_empty = True
                logger.debug("Done")
        else:
            mask = resample_mask(mask, to=image)
            false_mask = copy.deepcopy(mask)  # Used to initialize the extractors
            false_mask = apply_numpy_fn(false_mask, add_pos, output_is_mask=True)
            self.extractors = {extractor_name: AVAILABLE_EXTRACTORS[extractor_name](image, false_mask)
                                for extractor_name in AVAILABLE_EXTRACTORS}
            self.mask_is_empty = True

    
    def get_feature_vector(self):
        features = {}
        for extractor_name in self.extractors:
            for method_name, method in inspect.getmembers(self.extractors[extractor_name], is_feat_method):
                if method_name.startswith("get") and method_name.endswith("FeatureValue"):
                    if not hasattr(method, "_is_deprecated"):
                        if not self.mask_is_empty:
                            try:
                                features[f"{extractor_name}_{method_name[3:-12]}"] = method()[0]
                            except (IndexError, TypeError):
                                features[f"{extractor_name}_{method_name[3:-12]}"] = method()
                        else:  # Mask is empty
                            logger.warning(f"Empty mask found!")
                            features[f"{extractor_name}_{method_name[3:-12]}"] = np.nan
                    else:
                        pass
                        logger.debug(f"{method_name} is deprecated")
        return features

if __name__ == "__main__":
    test_image = load_image("../../data/Dataset001_Test/imagesTr/CT_Abdo_001_0000.nii.gz")
    test_mask = load_mask("../../data/Dataset001_Test/labelsTr/CT_Abdo_001.nii.gz", label=3)
    re = Radiomics_Extractor(test_image, test_mask)
    feature_vector = re.get_feature_vector()
    print(feature_vector)
    print(f"{len(feature_vector)} Features were extracted")
