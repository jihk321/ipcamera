import tensorflow as tf
import torch
import types 
print(torch.cuda.is_available())
print(tf.__version__)


ooo = types.SimpleNamespace()
ooo.a = 1

print(ooo.a)