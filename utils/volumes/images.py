import SimpleITK as sitk


def load_image(image_path, dtype=None):
    if dtype is not None:
        return sitk.ReadImage(image_path, outputPixelType=dtype)
    else:
        return sitk.ReadImage(image_path)


def apply_numpy_fn(image, fn, output_is_image=True):
    image_np = sitk.GetArrayFromImage(image)
    out = fn(image_np)
    if output_is_image:
        image_out = sitk.GetImageFromArray(out)
        image_out.CopyInformation(image)
        return image_out
    else:
        return out


def resample_image(image, to):
    resampler = sitk.ResampleImageFilter()
    resampler.SetInterpolator(sitk.sitkBSpline)
    resampler.SetOutputDirection(to.GetDirection())
    resampler.SetOutputOrigin(to.GetOrigin())
    resampler.SetSize(to.GetSize())
    resampler.SetOutputSpacing(to.GetSpacing())
    resampled_image = resampler.Execute(image)
    return resampled_image

def resample_image_to_spacing(image, spacing):
    new_size = [l* round(j/i) for i, j, l in zip(spacing, image.GetSpacing(), image.GetSize())]
    resampler = sitk.ResampleImageFilter()
    resampler.SetInterpolator(sitk.sitkBSpline)
    resampler.SetOutputDirection(image.GetDirection())
    resampler.SetOutputOrigin(image.GetOrigin())
    resampler.SetSize(new_size)
    resampler.SetOutputSpacing(spacing)
    resampled_image = resampler.Execute(image)
    return resampled_image
    


if __name__ == "__main__":
    import numpy as np
    ct = load_image("../../data/Dataset001_Test/imagesTr/CT_Abdo_001_0000.nii.gz")
    pet = load_image("../../data/Dataset001_Test/imagesTr/CT_Abdo_001_0001.nii.gz")
    resample_image(ct, pet)
    assert ct.GetSpacing() == pet.GetSpacing()
    assert ct.GetSize() == pet.GetSize()
    assert ct.GetOrigin() == pet.GetOrigin()
    assert ct.GetDirection() == pet.GetDirection()
    max_val = apply_numpy_fn(ct, lambda x: np.max(x), output_is_image=False)
    assert isinstance(max_val, np.int16)
    print("All tests OK")