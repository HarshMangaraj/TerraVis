import rasterio
import numpy as np

with rasterio.open("landsat_data/LC09_L2SP_140046_20260616_02_T1_thermal.TIF") as src:
    thermal = src.read(1, window=((1000, 1256), (1000, 1256))).astype(np.float32)

thermal = (thermal - thermal.min()) / (thermal.max() - thermal.min() + 1e-6)
thermal = thermal[..., np.newaxis]

np.save("test_thermal_patch.npy", thermal)
print("Saved, shape:", thermal.shape)