import numpy as np
import SimpleITK as sitk


def load_mask(mask_path, label, dtype=sitk.sitkUInt8):
    """Loads a binary or multilabel mask from a file using SimpleITK.

    Args:
        mask_path (str): 
        label (Union[str | int]): if label is 'all', return all nonzero elements fused together
          as a single label labeled 1. If label is 'each', return the mask as is, with all labels.
          If label is of type int,returns thhe binary mask for the corresponding label.
        dtype (type, optional): Data type of the returned object. Defaults to sitk.sitkUInt8.

    Returns:
        _type_: _description_
    """
    # Load mask from file
    mask = sitk.ReadImage(mask_path, outputPixelType=dtype)
    
    if isinstance(label, str):
        if label =="all":  # Fuse all labels together and assign it class 1
            mask_np = sitk.GetArrayFromImage(mask)
            np_type = mask_np.dtype

            # This line is important the rest is ensuring the proper data type and spatial info
            mask_np_all = (mask_np > 0).astype(np_type) * 1  # Fuse all labels greater than 0
            
            mask_all = sitk.GetImageFromArray(mask_np_all)
            mask_all.CopyInformation(mask)
            mask_all = sitk.Cast(mask_all, dtype)
            return mask_all
        elif label == "each":
            return mask
    else:
        mask_np = sitk.GetArrayFromImage(mask)
        np_type = mask_np.dtype
        mask_np_class = (mask_np == label).astype(np_type) * 1  # Keep only the targeted label
        mask_class= sitk.GetImageFromArray(mask_np_class)
        mask_class.CopyInformation(mask)
        mask_class = sitk.Cast(mask_class, dtype)

        return mask_class

def bb_sitk(image: sitk.Image, label=1):
    bbox = sitk.LabelShapeStatisticsImageFilter()
    bbox.Execute(image)
    return bbox.GetBoundingBox(label)


def get_bb_coords(mask: np.ndarray):
    """Get the bounding box coordinates as xmin, xmax, ymin, ymax, zmin, zmax

    Args:
        mask (np.ndarray): multilabel or binary mask

    Returns:
        tuple: A tuple of bounding box coordinates
    """
    aw = np.argwhere(mask > 0)
    try:
        xs = aw[:, 0]
        ys = aw[:, 1]
        zs = aw[:, 2]
        x_min, x_max = np.min(xs), np.max(xs)
        y_min, y_max = np.min(ys), np.max(ys)
        z_min, z_max = np.min(zs), np.max(zs)
    except ValueError as e:
        print(f"Following error occurred: {e}"
              f"Reverting to full")
        print(np.unique(mask))
        x, y, z = np.shape(mask)
        return (0, x, 0, y, 0, z)
    return (x_min, x_max, y_min, y_max, z_min, z_max)


def apply_numpy_fn(mask, fn, output_is_mask=True):
    mask_np = sitk.GetArrayFromImage(mask)
    out = fn(mask_np)
    if output_is_mask:
        mask_out = sitk.GetImageFromArray(out)
        mask_out.CopyInformation(mask)
        return mask_out
    else:
        return out

def add_pos(mask):
    mask[0,0,0] = 1
    return mask

def apply_bbox(mask, bbox):
    xmin, xmax, ymin, ymax, zmin, zmax = bbox
    return mask[xmin:xmax, ymin:ymax, zmin:zmax]


def resample_mask(mask, to):
    if isinstance(to, sitk.Image):
        resampler = sitk.ResampleImageFilter()
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        resampler.SetOutputSpacing(to.GetSpacing())
        resampler.SetOutputDirection(to.GetDirection())
        resampler.SetOutputOrigin(to.GetOrigin())
        resampler.SetSize(to.GetSize())
        resampled_image = resampler.Execute(mask)
    elif isinstance(to, (tuple, list)):
        new_size = tuple([round(i*(j/k)) for i,j,k in zip(mask.GetSize(), mask.GetSpacing(), to)])
        resampler = sitk.ResampleImageFilter()
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        resampler.SetOutputSpacing(to)
        resampler.SetOutputDirection(mask.GetDirection())
        resampler.SetOutputOrigin(mask.GetOrigin())
        resampler.SetSize(new_size)
        resampled_image = resampler.Execute(mask)
    else:
        raise TypeError(f"to must be a SimpleITK.Image or a 3D tuple or list, found {to}")
    return resampled_image


if __name__ == "__main__":
    mask_each = load_mask("../../data/Dataset001_Test/labelsTr/CT_Abdo_001.nii.gz", label="each")
    mask_each_np = sitk.GetArrayFromImage(mask_each)

    mask_all = load_mask("../../data/Dataset001_Test/labelsTr/CT_Abdo_001.nii.gz", label="all")
    mask_all_np = sitk.GetArrayFromImage(mask_all)

    mask_1 = load_mask("../../data/Dataset001_Test/labelsTr/CT_Abdo_001.nii.gz", label=1)
    mask_1_np = sitk.GetArrayFromImage(mask_1)

    mask_2 = load_mask("../../data/Dataset001_Test/labelsTr/CT_Abdo_001.nii.gz", label=2)
    mask_2_np = sitk.GetArrayFromImage(mask_2)

    mask_3 = load_mask("../../data/Dataset001_Test/labelsTr/CT_Abdo_001.nii.gz", label=3)
    mask_3_np = sitk.GetArrayFromImage(mask_3)

    assert mask_1_np.sum() + mask_2_np.sum() + mask_3_np.sum() == mask_all_np.sum()
    assert mask_1_np.sum()*1 + mask_2_np.sum()*2 + mask_3_np.sum()*3 == mask_each_np.sum()
