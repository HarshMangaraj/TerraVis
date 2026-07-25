import numpy as np
import rasterio
import albumentations as A
from torch.utils.data import Dataset


class SatelliteDataset(Dataset):
    """
    Base class: knows how to read a fixed list of (row, col) patch windows
    from a set of band files, and apply augmentation. Subclasses only need
    to define HOW input/target pairs are constructed for their specific task.
    """

    def __init__(self, patch_coords, patch_size=256, augment=True):
        self.patch_coords = patch_coords
        self.patch_size = patch_size
        self.augment = augment

        self.transform = A.Compose([
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomBrightnessContrast(p=0.3, brightness_limit=0.1, contrast_limit=0.1),
        ])

    def __len__(self):
        return len(self.patch_coords)

    def _read_window(self, path, row, col):
        window = ((row, row + self.patch_size), (col, col + self.patch_size))
        with rasterio.open(path) as src:
            return src.read(1, window=window)

    def _apply_augment(self, input_arr, target_arr):
        if not self.augment:
            return input_arr, target_arr
        result = self.transform(image=input_arr, mask=target_arr)
        return result["image"], result["mask"]

    def __getitem__(self, idx):
        raise NotImplementedError("Subclasses must implement __getitem__")


class LISSIVDataset(SatelliteDataset):
    """
    PS2: cloud removal. Builds synthetic cloudy/clear pairs from a single
    clear Sentinel-2 patch, by pasting a real cloud shape onto a clean patch.
    """

    def __init__(self, base_path, clear_coords, cloud_source_coords, patch_size=256, augment=True):
        super().__init__(clear_coords, patch_size, augment)
        self.base_path = base_path
        self.cloud_source_coords = cloud_source_coords

    def __getitem__(self, idx):
        row, col = self.patch_coords[idx]

        red = self._read_window(f"{self.base_path}/R10m/T45QUC_20241207T045201_B04_10m.jp2", row, col)
        green = self._read_window(f"{self.base_path}/R10m/T45QUC_20241207T045201_B03_10m.jp2", row, col)
        blue = self._read_window(f"{self.base_path}/R10m/T45QUC_20241207T045201_B02_10m.jp2", row, col)
        target = np.stack([red, green, blue], axis=-1).astype(np.float32) / 3000.0
        target = np.clip(target, 0, 1)

        cloud_row, cloud_col = self.cloud_source_coords[idx % len(self.cloud_source_coords)]
        cloud_mask_window = ((cloud_row // 2, cloud_row // 2 + self.patch_size // 2),
                              (cloud_col // 2, cloud_col // 2 + self.patch_size // 2))
        with rasterio.open(f"{self.base_path}/R20m/T45QUC_20241207T045201_SCL_20m.jp2") as src:
            scl_patch = src.read(1, window=cloud_mask_window)
        cloud_mask = np.isin(scl_patch, [3, 8, 9, 10]).astype(np.uint8)
        cloud_mask = np.repeat(np.repeat(cloud_mask, 2, axis=0), 2, axis=1)
        cloud_mask = cloud_mask[:self.patch_size, :self.patch_size]

        input_patch = target.copy()
        input_patch[cloud_mask.astype(bool)] = [1.0, 1.0, 1.0]

        input_patch, target = self._apply_augment(input_patch, target)
        return input_patch, target


class LandsatDataset(SatelliteDataset):
    """PS10: IR colorization. Input = thermal Band 10 (1 channel),
    Target = RGB Bands 4/3/2 stacked (3 channels)."""

    def __init__(self, base_path, patch_coords, patch_size=256, augment=True):
        super().__init__(patch_coords, patch_size, augment)
        self.base_path = base_path
    def __getitem__(self, idx):
        row, col = self.patch_coords[idx]

        thermal = self._read_window(f"{self.base_path}_thermal.TIF", row, col).astype(np.float32)
        thermal = (thermal - thermal.min()) / (thermal.max() - thermal.min() + 1e-6)
        thermal = thermal[..., np.newaxis]

        red = self._read_window(f"{self.base_path}_red.TIF", row, col).astype(np.float32)
        green = self._read_window(f"{self.base_path}_green.TIF", row, col).astype(np.float32)
        blue = self._read_window(f"{self.base_path}_blue.TIF", row, col).astype(np.float32)
        rgb = np.stack([red, green, blue], axis=-1)
        rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min() + 1e-6)

        thermal, rgb = self._apply_augment(thermal, rgb)
        return thermal, rgb