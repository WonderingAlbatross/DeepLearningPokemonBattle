import ast
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class ANN(nn.Module):
    def __init__(self, input_size,l1_size,l2_size):
        super(ANN, self).__init__()
        self.fc1 = nn.Linear(input_size, l1_size)  
        self.fc2 = nn.Linear(l1_size, l2_size)          
        self.fc3 = nn.Linear(l2_size, 1)            

    def forward(self, x):
        x = nn.functional.relu(self.fc1(x))
        x = nn.functional.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))  
        return x


model = torch.load('model_256_128.pth')
X_tensor = torch.load('X_vectorized_test01.pt').to("cuda")

l = len(X_tensor)



def index_vector(i):
    v = [0]*50
    v[i] = 1
    return v

def pokemon_vector(i):
    X_tensor[:,13:63] = torch.tensor([index_vector(i)]*l).to("cuda")

    return model(X_tensor).squeeze(1)


pv = []
norm = []
s = []
for i in range(50):
    print(i)
    pv.append(1-2*pokemon_vector(i)) 
    norm.append(torch.norm(pv[i]).item())
    s.append(torch.sum(pv[i]).item())

distance = {}
for i in range(49):
    for j in range(i+1,50):
        distance[(i,j)] = (torch.dot(pv[i],pv[j])/norm[i]/norm[j]).item()


d_list = list(distance.keys())
d_list.sort(key = lambda x: distance[x])

s.sort()
print(d_list)
print([distance[x] for x in d_list])
print(s)

