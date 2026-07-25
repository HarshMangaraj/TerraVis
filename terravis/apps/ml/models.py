import torch
import torch.nn as nn


class UNetBlock(nn.Module):
    """One encoder or decoder block of the U-Net generator."""
    def __init__(self, in_ch, out_ch, down=True, use_dropout=False):
        super().__init__()
        if down:
            self.conv = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 4, 2, 1, bias=False),
                nn.BatchNorm2d(out_ch),
                nn.LeakyReLU(0.2),
            )
        else:
            self.conv = nn.Sequential(
                nn.ConvTranspose2d(in_ch, out_ch, 4, 2, 1, bias=False),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(),
            )
        self.use_dropout = use_dropout
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.conv(x)
        return self.dropout(x) if self.use_dropout else x


class Generator(nn.Module):
    """U-Net generator: encoder downsamples, decoder upsamples, skip connections
    preserve fine spatial detail that would otherwise be lost at the bottleneck."""
    def __init__(self, in_channels=3, out_channels=3, features=64):
        super().__init__()
        self.down1 = nn.Sequential(nn.Conv2d(in_channels, features, 4, 2, 1), nn.LeakyReLU(0.2))
        self.down2 = UNetBlock(features, features * 2)
        self.down3 = UNetBlock(features * 2, features * 4)
        self.down4 = UNetBlock(features * 4, features * 8)
        self.bottleneck = nn.Sequential(nn.Conv2d(features * 8, features * 8, 4, 2, 1), nn.ReLU())

        self.up1 = UNetBlock(features * 8, features * 8, down=False, use_dropout=True)
        self.up2 = UNetBlock(features * 16, features * 4, down=False, use_dropout=True)
        self.up3 = UNetBlock(features * 8, features * 2, down=False)
        self.up4 = UNetBlock(features * 4, features, down=False)
        self.final = nn.Sequential(
            nn.ConvTranspose2d(features * 2, out_channels, 4, 2, 1),
            nn.Tanh(),
        )

    def forward(self, x):
        d1 = self.down1(x)
        d2 = self.down2(d1)
        d3 = self.down3(d2)
        d4 = self.down4(d3)
        b = self.bottleneck(d4)

        u1 = self.up1(b)
        # skip connections: concatenate encoder output with matching decoder input
        u2 = self.up2(torch.cat([u1, d4], dim=1))
        u3 = self.up3(torch.cat([u2, d3], dim=1))
        u4 = self.up4(torch.cat([u3, d2], dim=1))
        return self.final(torch.cat([u4, d1], dim=1))


class Discriminator(nn.Module):
    """PatchGAN: judges overlapping 70x70 patches rather than the whole image,
    which produces sharper textures and more stable training than a single
    real/fake verdict for the entire image."""
    def __init__(self, in_channels=6, features=64):  # 6 = input(3) + target/output(3) concatenated
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(in_channels, features, 4, 2, 1), nn.LeakyReLU(0.2),
            nn.Conv2d(features, features * 2, 4, 2, 1), nn.BatchNorm2d(features * 2), nn.LeakyReLU(0.2),
            nn.Conv2d(features * 2, features * 4, 4, 2, 1), nn.BatchNorm2d(features * 4), nn.LeakyReLU(0.2),
            nn.Conv2d(features * 4, features * 8, 4, 1, 1), nn.BatchNorm2d(features * 8), nn.LeakyReLU(0.2),
            nn.Conv2d(features * 8, 1, 4, 1, 1),  # outputs a grid of patch-level real/fake scores
        )

    def forward(self, x, y):
        return self.model(torch.cat([x, y], dim=1))