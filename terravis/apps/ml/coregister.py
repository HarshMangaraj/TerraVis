import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np

base = "extracted/S2A_MSIL2A_20241207T045201_N0511_R076_T45QUC_20241207T074151.SAFE/GRANULE/L2A_T45QUC_A049408_20241207T050111/IMG_DATA"

red_path = f"{base}/R10m/T45QUC_20241207T045201_B04_10m.jp2"
scl_path = f"{base}/R20m/T45QUC_20241207T045201_SCL_20m.jp2"

# Open the "target" (reference) grid we want to match — the 10m RGB grid
with rasterio.open(red_path) as ref:
    ref_transform = ref.transform   # maps pixel coords -> real-world coords
    ref_crs = ref.crs
    ref_shape = (ref.height, ref.width)

# Open the source (SCL, 20m) that we want to resample onto the reference grid
with rasterio.open(scl_path) as src:
    scl_data = src.read(1)
    src_transform = src.transform
    src_crs = src.crs

# Destination array, sized to match the REFERENCE grid exactly
scl_aligned = np.empty(ref_shape, dtype=scl_data.dtype)

reproject(
    source=scl_data,
    destination=scl_aligned,
    src_transform=src_transform,
    src_crs=src_crs,
    dst_transform=ref_transform,
    dst_crs=ref_crs,
    resampling=Resampling.nearest,  # nearest-neighbor: correct choice for CATEGORICAL data like SCL codes
)

print("Original SCL shape:", scl_data.shape)
print("Aligned SCL shape:", scl_aligned.shape)
print("Aligned matches reference shape:", scl_aligned.shape == ref_shape)

# Sanity check: cloud percentage should be very close to what we got before
cloud_mask = np.isin(scl_aligned, [3, 8, 9, 10])
print("Percent flagged as cloud-related (proper reproject):", 100 * cloud_mask.sum() / cloud_mask.size)