import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import csv
import os

from models import Generator, Discriminator
from dataset import LISSIVDataset

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("Training on:", DEVICE)

def to_tensor_chw(batch):
    # (B, H, W, C) numpy/torch -> (B, C, H, W), and rescale [0,1] -> [-1,1] for Tanh output
    return (batch.permute(0, 3, 1, 2).float() * 2 - 1)


def train(base_path, epochs=5, batch_size=2, lr=2e-4, out_dir="checkpoints"):
    os.makedirs(out_dir, exist_ok=True)

    clear_coords = [(4000, 7000), (4200, 7200), (4400, 7400), (4600, 7600)]
    cloud_coords = [(4000, 7000), (4100, 7100), (4050, 7300)]
    dataset = LISSIVDataset(base_path, clear_coords, cloud_coords, patch_size=256, augment=True)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    gen = Generator().to(DEVICE)
    disc = Discriminator().to(DEVICE)

    opt_gen = optim.Adam(gen.parameters(), lr=lr, betas=(0.5, 0.999))
    opt_disc = optim.Adam(disc.parameters(), lr=lr, betas=(0.5, 0.999))

    bce = nn.BCEWithLogitsLoss()  # adversarial loss
    l1 = nn.L1Loss()              # reconstruction loss (pixel-level accuracy)
    L1_LAMBDA = 100  # weight L1 heavily — standard Pix2Pix setting, keeps output close to ground truth

    log_path = f"{out_dir}/loss_log.csv"
    with open(log_path, "w", newline="") as f:
        csv.writer(f).writerow(["epoch", "gen_loss", "disc_loss"])

    for epoch in range(epochs):
        epoch_gen_loss, epoch_disc_loss = 0, 0
        for input_batch, target_batch in loader:
            x = to_tensor_chw(input_batch).to(DEVICE)
            y = to_tensor_chw(target_batch).to(DEVICE)

            # --- Train Discriminator ---
            y_fake = gen(x)
            d_real = disc(x, y)
            d_fake = disc(x, y_fake.detach())
            d_loss_real = bce(d_real, torch.ones_like(d_real))
            d_loss_fake = bce(d_fake, torch.zeros_like(d_fake))
            d_loss = (d_loss_real + d_loss_fake) / 2

            opt_disc.zero_grad()
            d_loss.backward()
            opt_disc.step()

            # --- Train Generator ---
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

        if (epoch + 1) % 5 == 0 or epoch == epochs - 1:
            torch.save(gen.state_dict(), f"{out_dir}/generator_epoch{epoch+1}.pth")

    return gen


if __name__ == "__main__":
    base = "extracted/S2A_MSIL2A_20241207T045201_N0511_R076_T45QUC_20241207T074151.SAFE/GRANULE/L2A_T45QUC_A049408_20241207T050111/IMG_DATA"
    train(base, epochs=5, batch_size=2)