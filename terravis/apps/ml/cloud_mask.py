import rasterio
import numpy as np
import matplotlib.pyplot as plt

base = "extracted/S2A_MSIL2A_20241207T045201_N0511_R076_T45QUC_20241207T074151.SAFE/GRANULE/L2A_T45QUC_A049408_20241207T050111/IMG_DATA"

scl_path = f"{base}/R20m/T45QUC_20241207T045201_SCL_20m.jp2"
red_path = f"{base}/R10m/T45QUC_20241207T045201_B04_10m.jp2"   # Red
green_path = f"{base}/R10m/T45QUC_20241207T045201_B03_10m.jp2" # Green
blue_path = f"{base}/R10m/T45QUC_20241207T045201_B02_10m.jp2"  # Blue

# Read RGB bands (10m resolution, full size)
with rasterio.open(red_path) as src:
    red = src.read(1)
with rasterio.open(green_path) as src:
    green = src.read(1)
with rasterio.open(blue_path) as src:
    blue = src.read(1)

# Read SCL band (20m resolution — HALF the pixel count of the RGB bands)
with rasterio.open(scl_path) as src:
    scl = src.read(1)

print("RGB shape:", red.shape)
print("SCL shape:", scl.shape)

# Cloud-related SCL codes: 3=shadow, 8=cloud medium, 9=cloud high, 10=thin cirrus
cloud_mask = np.isin(scl, [3, 8, 9, 10])
print("Percent of scene flagged as cloud-related:", 100 * cloud_mask.sum() / cloud_mask.size)

# Stack RGB into a normal image array, scaling uint16 -> 0-1 range for display
# (dividing by 3000 is a common quick-and-dirty stretch for Sentinel-2 true-color previews)
rgb = np.stack([red, green, blue], axis=-1).astype(np.float32) / 3000.0
rgb = np.clip(rgb, 0, 1)

# Upsample the cloud mask to match RGB resolution (20m -> 10m is a simple 2x repeat)
cloud_mask_upsampled = np.repeat(np.repeat(cloud_mask, 2, axis=0), 2, axis=1)
# Trim/pad in case of off-by-one size mismatch after upsampling
cloud_mask_upsampled = cloud_mask_upsampled[:rgb.shape[0], :rgb.shape[1]]

# Plot side by side: original RGB, and RGB with cloud mask overlaid in red
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
axes[0].imshow(rgb)
axes[0].set_title("Original RGB")
axes[0].axis("off")

overlay = rgb.copy()
overlay[cloud_mask_upsampled] = [1, 0, 0]  # paint cloud pixels bright red
axes[1].imshow(overlay)
axes[1].set_title("Cloud Mask Overlay (red = masked)")
axes[1].axis("off")

plt.tight_layout()
plt.savefig("cloud_mask_result.png", dpi=150)
print("Saved visualization to cloud_mask_result.png")