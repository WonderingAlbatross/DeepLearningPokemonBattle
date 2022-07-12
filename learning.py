import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
import pandas as pd
import time
import matplotlib.pyplot as plt
import os

class ANNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim_1, hidden_dim_2, hidden_dim_3, output_dim):
        super(ANNModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim_1) 
        self.ac1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim_1, hidden_dim_2) 
        self.ac2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_dim_2, hidden_dim_3)
        self.ac3 = nn.ReLU()
        self.fc4 = nn.Linear(hidden_dim_3, output_dim)  
    def forward(self, i):
        out = self.fc1(i)
        out = self.ac1(out)
        out = self.fc2(out)
        out = self.ac2(out)
        out = self.fc3(out)
        out = self.ac3(out)
        out = self.fc4(out) 
        return out


print(torch.cuda.is_available())
print(torch.cuda.device_count()) 
print(torch.cuda.current_device())
print(torch.cuda.get_device_name(0))
print("start loading data...")



start_time = time.time()



#df1.to_parquet("data.parquet", compression=None)


input_dim = 711
hidden_dim_1 = 500
hidden_dim_2 = 300
hidden_dim_3 = 100
output_dim = 1
learning_rate = 0.00001
error = nn.MSELoss()
batch_size = 1024
epoch = 5
filename = "data"





model = ANNModel(input_dim, hidden_dim_1, hidden_dim_2, hidden_dim_3,output_dim).cuda(0)
model.load_state_dict(torch.load("model - mix3"))
model.eval()

optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

df1 = pd.read_parquet(filename+".parquet")
df2 = pd.read_csv("test.csv",header=None)
data2 = torch.tensor(df2.to_numpy().astype(np.float32)[:,:input_dim]).cuda(0)
_target2 = np.array([df2.to_numpy().astype(np.float32)[:,input_dim]]).T
target2 = torch.tensor(_target2).cuda(0)


if os.path.isfile(filename+".parquet") == False:
	df = pd.read_csv(filename+".csv",header=0)
	df.to_parquet(filename+".parquet", compression=None)


sample_size = 102400





print("data loaded","time:",time.time()-start_time)
print("test MSE:",(_target2**2).mean())
fig = []
for num in range(epoch):
	for count in range(int(df1.shape[0] / sample_size)-1):
		#df1 = pd.read_parquet(filename+".parquet").sample(sample_size,random_state=int(time.time())).to_numpy().astype(np.float32)	
		_dt = df1[count*sample_size:(count+1)*sample_size].to_numpy().astype(np.float32)
		_target = torch.tensor(_dt[:,input_dim]).cuda(0)
		target = torch.reshape(_target,(_target.size(dim=0),1))
		data = torch.tensor(_dt[:,:input_dim]).cuda(0)
		train = torch.utils.data.TensorDataset(data, target)
		train_loader = torch.utils.data.DataLoader(train, batch_size = batch_size,shuffle = True)
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
	print(loss.cpu().detach().numpy(),loss2.cpu().detach().numpy().astype(np.float32))
	print(num+1,time.time()-start_time)
	fig += [[loss.cpu().detach().numpy(),loss2.cpu().detach().numpy().astype(np.float32),num+1]]
	




fig = np.array(fig)
torch.save(model.state_dict(), "model - mix3")


plt.figure()
plt.plot(
    fig[:,2],
    fig[:,0],
    label="data_loss"
)

plt.plot(
    fig[:,2],
    fig[:,1],
    label="test_loss"
)
plt.legend()
plt.show()

