import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import csv
import os

from models import Generator, Discriminator
from dataset import LandsatDataset

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("Training on:", DEVICE)

def to_tensor_chw(batch):
    return (batch.permute(0, 3, 1, 2).float() * 2 - 1)


def train_ps10(base_path, epochs=5, batch_size=2, lr=2e-4, out_dir="checkpoints"):
    os.makedirs(out_dir, exist_ok=True)

    # Patch coords well within the 7681x7821 scene bounds
    patch_coords = [(1000, 1000), (1500, 1500), (2000, 2000), (2500, 2500), (3000, 3000)]
    dataset = LandsatDataset(base_path, patch_coords, patch_size=256, augment=True)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Generator input is 1 channel (thermal), output is 3 channels (RGB)
    gen = Generator(in_channels=1, out_channels=3).to(DEVICE)
    # Discriminator sees input(1ch) + target/output(3ch) concatenated = 4 channels
    disc = Discriminator(in_channels=4).to(DEVICE)

    opt_gen = optim.Adam(gen.parameters(), lr=lr, betas=(0.5, 0.999))
    opt_disc = optim.Adam(disc.parameters(), lr=lr, betas=(0.5, 0.999))

    bce = nn.BCEWithLogitsLoss()
    l1 = nn.L1Loss()
    L1_LAMBDA = 100

    log_path = f"{out_dir}/ps10_loss_log.csv"
    with open(log_path, "w", newline="") as f:
        csv.writer(f).writerow(["epoch", "gen_loss", "disc_loss"])

    for epoch in range(epochs):
        epoch_gen_loss, epoch_disc_loss = 0, 0
        for input_batch, target_batch in loader:
            x = to_tensor_chw(input_batch).to(DEVICE)  # (B, 1, H, W)
            y = to_tensor_chw(target_batch).to(DEVICE)  # (B, 3, H, W)

            y_fake = gen(x)
            d_real = disc(x, y)
            d_fake = disc(x, y_fake.detach())
            d_loss_real = bce(d_real, torch.ones_like(d_real))
            d_loss_fake = bce(d_fake, torch.zeros_like(d_fake))
            d_loss = (d_loss_real + d_loss_fake) / 2

            opt_disc.zero_grad()
            d_loss.backward()
            opt_disc.step()

            d_fake = disc(x, y_fake)
            g_adv_loss = bce(d_fake, torch.ones_like(d_fake))
            g_l1_loss = l1(y_fake, y) * L1_LAMBDA
            g_loss = g_adv_loss + g_l1_loss

            opt_gen.zero_grad()
            g_loss.backward()
            opt_gen.step()

            epoch_gen_loss += g_loss.item()
            epoch_disc_loss += d_loss.item()

        avg_g = epoch_gen_loss / len(loader)
        avg_d = epoch_disc_loss / len(loader)
        print(f"Epoch {epoch+1}/{epochs} — Gen loss: {avg_g:.4f}, Disc loss: {avg_d:.4f}")

        with open(log_path, "a", newline="") as f:
            csv.writer(f).writerow([epoch + 1, avg_g, avg_d])

    torch.save(gen.state_dict(), f"{out_dir}/generator_ps10_epoch{epochs}.pth")
    return gen


if __name__ == "__main__":
    base = "landsat_data/LC09_L2SP_140046_20260616_02_T1"
    train_ps10(base, epochs=5, batch_size=2)