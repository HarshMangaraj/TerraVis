import torch
from models import Generator, Discriminator

gen = Generator()
disc = Discriminator()

x = torch.randn(1, 3, 256, 256)
gen_out = gen(x)
print("Generator output shape:", gen_out.shape)  # should be (1, 3, 256, 256)

disc_out = disc(x, gen_out)
print("Discriminator output shape:", disc_out.shape)  # should be (1, 1, 30, 30) roughly