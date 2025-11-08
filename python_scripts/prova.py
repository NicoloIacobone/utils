import torch

# Carica il file "2.pt"
tensor = torch.load("2.pt")

# Stampa la shape
print(tensor.shape)