import rasterio
import numpy as np
from PIL import Image, ImageFilter

base = "extracted/S2A_MSIL2A_20241207T045201_N0511_R076_T45QUC_20241207T074151.SAFE/GRANULE/L2A_T45QUC_A049408_20241207T050111/IMG_DATA/R10m"

with rasterio.open(f"{base}/T45QUC_20241207T045201_B04_10m.jp2") as src:
    red = src.read(1, out_shape=(2048, 2048))
with rasterio.open(f"{base}/T45QUC_20241207T045201_B03_10m.jp2") as src:
    green = src.read(1, out_shape=(2048, 2048))
with rasterio.open(f"{base}/T45QUC_20241207T045201_B02_10m.jp2") as src:
    blue = src.read(1, out_shape=(2048, 2048))

rgb = np.stack([red, green, blue], axis=-1).astype(np.float32) / 3000.0  # same stretch as earlier sessions
rgb = np.clip(rgb, 0, 1)
rgb = np.power(rgb, 0.85)  # mild brightening only, not aggressive

rgb_8bit = (rgb * 255).astype(np.uint8)

h, w = rgb_8bit.shape[:2]
alpha = np.full((h, w), 255, dtype=np.uint8)
feather = 60
for i in range(feather):
    factor = i / feather
    alpha[i, :] = np.minimum(alpha[i, :], int(255 * factor))
    alpha[-(i + 1), :] = np.minimum(alpha[-(i + 1), :], int(255 * factor))
    alpha[:, i] = np.minimum(alpha[:, i], int(255 * factor))
    alpha[:, -(i + 1)] = np.minimum(alpha[:, -(i + 1)], int(255 * factor))

rgba = np.dstack([rgb_8bit, alpha])
img = Image.fromarray(rgba, mode="RGBA")
img = img.filter(ImageFilter.SMOOTH)
img.save("scene_overlay.png")
print("Saved, size:", img.size)