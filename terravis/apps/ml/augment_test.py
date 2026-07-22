import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import albumentations as A
import matplotlib.pyplot as plt

base = "extracted/S2A_MSIL2A_20241207T045201_N0511_R076_T45QUC_20241207T074151.SAFE/GRANULE/L2A_T45QUC_A049408_20241207T050111/IMG_DATA"

# Load a small patch instead of the full 10980x10980 image — much faster to work with
window = ((2000, 2512), (2000, 2512))  # a 512x512 pixel crop

with rasterio.open(f"{base}/R10m/T45QUC_20241207T045201_B04_10m.jp2") as src:
    red = src.read(1, window=window)
with rasterio.open(f"{base}/R10m/T45QUC_20241207T045201_B03_10m.jp2") as src:
    green = src.read(1, window=window)
with rasterio.open(f"{base}/R10m/T45QUC_20241207T045201_B02_10m.jp2") as src:
    blue = src.read(1, window=window)

rgb_patch = np.stack([red, green, blue], axis=-1).astype(np.float32) / 3000.0
rgb_patch = np.clip(rgb_patch, 0, 1)

with rasterio.open(f"{base}/R20m/T45QUC_20241207T045201_SCL_20m.jp2") as src:
    scl_full = src.read(1)
cloud_mask_full = np.isin(scl_full, [3, 8, 9, 10]).astype(np.uint8)
# Upsample crudely just for this test (SCL half-resolution window)
cloud_mask_full = np.repeat(np.repeat(cloud_mask_full, 2, axis=0), 2, axis=1)
mask_patch = cloud_mask_full[2000:2512, 2000:2512]

# Define the augmentation pipeline
transform = A.Compose([
    A.HorizontalFlip(p=1.0),   # p=1.0 forces it ON every time, for this demo
    A.VerticalFlip(p=1.0),
    A.RandomRotate90(p=1.0),
    A.RandomBrightnessContrast(p=1.0, brightness_limit=0.2, contrast_limit=0.2),
])

# KEY LINE: passing image + mask together guarantees the SAME random transform hits both
result = transform(image=rgb_patch, mask=mask_patch)
aug_image = result["image"]
aug_mask = result["mask"]

# Visualize original vs augmented pairs side by side
fig, axes = plt.subplots(2, 2, figsize=(10, 10))
axes[0, 0].imshow(rgb_patch); axes[0, 0].set_title("Original RGB patch"); axes[0, 0].axis("off")
axes[0, 1].imshow(mask_patch, cmap="Reds"); axes[0, 1].set_title("Original mask"); axes[0, 1].axis("off")
axes[1, 0].imshow(aug_image); axes[1, 0].set_title("Augmented RGB patch"); axes[1, 0].axis("off")
axes[1, 1].imshow(aug_mask, cmap="Reds"); axes[1, 1].set_title("Augmented mask (must match!)"); axes[1, 1].axis("off")
plt.tight_layout()
plt.savefig("augment_result.png", dpi=150)
print("Saved to augment_result.png")