import torch

# Carica il file "2.pt"
tensor = torch.load("2.pt")

# Stampa la shape
print(tensor.shape)
print("Student type:", type(tensor))
print("Student requires_grad:", getattr(tensor, "requires_grad", None))