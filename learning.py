import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
import pandas as pd
import time


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


print(torch.cuda.is_available())
print(torch.cuda.device_count()) 
print(torch.cuda.current_device())
print(torch.cuda.get_device_name(0))
print("start loading data...")



start_time = time.time()
df1 = pd.read_parquet("data.parquet")
df2 = pd.read_csv("testdata.csv",header=None)


#df1.to_parquet("data.parquet", compression=None)


input_dim = 711
hidden_dim = 500
output_dim = 1
learning_rate = 0.0001
error = nn.MSELoss()
batch_size = 128
epoch = 100






model = ANNModel(input_dim, hidden_dim, output_dim).cuda(0)
model.load_state_dict(torch.load("model - 500"))
model.eval()

optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

data = torch.tensor(df1.to_numpy().astype(np.float32)[:,:input_dim]).cuda(0)
target = torch.tensor(np.array([df1.to_numpy().astype(np.float32)[:,input_dim]]).T).cuda(0)

data2 = torch.tensor(df2.to_numpy().astype(np.float32)[:,:input_dim]).cuda(0)
target2 = torch.tensor(np.array([df2.to_numpy().astype(np.float32)[:,input_dim]]).T).cuda(0)

train = torch.utils.data.TensorDataset(data, target)
train_loader = torch.utils.data.DataLoader(train, batch_size = batch_size,shuffle = True)

print("data loaded","time:",time.time()-start_time)



for num in range(epoch):
	for _data , _target in train_loader:
		optimizer.zero_grad()
		outputs = model(_data)
		loss = error(outputs, _target)
		loss.backward()
		optimizer.step()

	outputs = model(data)
	outputs2 = model(data2)
	loss = error(outputs, target)
	loss2 = error(outputs2, target2)
	print(loss.cpu().detach().numpy(),loss2.cpu().detach().numpy())
	print(num+1,"/",epoch,time.time()-start_time)

print(outputs2.cpu().detach().numpy())


torch.save(model.state_dict(), "model - 500")


'''
model = TheModelClass(*args, **kwargs)
model.load_state_dict(torch.load(PATH))
model.eval()
'''