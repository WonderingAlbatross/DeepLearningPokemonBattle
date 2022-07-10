import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
import pandas as pd
'''
print(torch.cuda.is_available())
print(torch.cuda.device_count()) 
print(torch.cuda.current_device())
print(torch.cuda.get_device_name(0))
'''
df1 = pd.read_csv("data.csv",header=None)
df2 = pd.read_csv("testdata.csv",header=None)


input_dim = 711
hidden_dim = 500
output_dim = 1
learning_rate = 0.01
error = nn.MSELoss()

class ANNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(ANNModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim) 
        self.ac1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, hidden_dim) 
        self.ac2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_dim, output_dim)  
    def forward(self, i):
        out = self.fc1(i)
        out = self.ac1(out)
        out = self.fc2(out)
        out = self.ac2(out)
        out = self.fc3(out)
        return out


model = ANNModel(input_dim, hidden_dim, output_dim)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for count in range(1):
	for k in range(1,10):
		dt = df1.sample(n=100, random_state=np.random.RandomState()).to_numpy()
		data = torch.tensor(dt[:,:input_dim])
		target = torch.tensor(np.array([dt[:,input_dim]]).T)

		optimizer.zero_grad()
		outputs = model(data)
		loss = error(outputs, target)
		loss.backward()
		optimizer.step()

	dt = df2.sample(n=100, random_state=np.random.RandomState()).to_numpy()
	data = torch.tensor(dt[:,:input_dim])
	target = torch.tensor(np.array([dt[:,input_dim]]).T)
	outputs = model(data)
	loss = error(outputs, target)
	print(loss)

torch.save(model.state_dict(), "model")

'''
model = TheModelClass(*args, **kwargs)
model.load_state_dict(torch.load(PATH))
model.eval()
'''