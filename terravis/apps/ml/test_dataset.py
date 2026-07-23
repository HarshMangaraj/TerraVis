from dataset import LISSIVDataset
from torch.utils.data import DataLoader

base = "extracted/S2A_MSIL2A_20241207T045201_N0511_R076_T45QUC_20241207T074151.SAFE/GRANULE/L2A_T45QUC_A049408_20241207T050111/IMG_DATA"

# A few clear-ish patch locations (from the terrain side of the scene)
clear_coords = [(4000, 7000), (4200, 7200), (4400, 7400)]
# A few cloudy patch locations (from the earlier heavy-cloud region)
cloud_coords = [(2000, 2000), (2200, 2200)]

dataset = LISSIVDataset(base, clear_coords, cloud_coords, patch_size=256)
print("Dataset length:", len(dataset))

loader = DataLoader(dataset, batch_size=2, shuffle=True)
batch_input, batch_target = next(iter(loader))
print("Input batch shape:", batch_input.shape)
print("Target batch shape:", batch_target.shape)