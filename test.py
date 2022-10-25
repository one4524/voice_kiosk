import torch
import tensorflow as tf

device = torch.device('mps')
print(f" - device : {device}")
sample = torch.Tensor([[10, 20, 30], [30, 20, 10]])
print(f" - cpu tensor : ")
print(sample)
sample = sample.to(device)
print(f" - gpu tensor : ")
print(sample)

tf.__version__()

