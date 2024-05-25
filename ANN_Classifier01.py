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


def combine(row,switch_p1_p2):
    vec = ast.literal_eval(row['weather']) + ast.literal_eval(row['field']) + ast.literal_eval(row['condition'])
    p1,p2 = 'p1','p2'
    if switch_p1_p2:
        p1,p2 = 'p2','p1'
    for p in [p1,p2]:
        vec += ast.literal_eval(row[p]) + ast.literal_eval(row[p+'a']) + ast.literal_eval(row[p+'b']) + ast.literal_eval(row[p+'c']) + ast.literal_eval(row[p+'d'])
    return vec

def get_Tensor(df_path):
    if os.path.exists("X_"+df_path[:-3]+'pt') and os.path.exists("y_"+df_path[:-3]+'pt') and os.path.exists("w_"+df_path[:-3]+'pt'):
        print('load tensors from file',df_path[:-3]+'pt')
        X_tensor = torch.load("X_"+df_path[:-3]+'pt')
        y_tensor = torch.load("y_"+df_path[:-3]+'pt')
        weight_tensor = torch.load("w_"+df_path[:-3]+'pt')
        return X_tensor.to(device), y_tensor.to(device), weight_tensor.to(device)

    print('creating tensors...',df_path[:-3]+'pt')
    df = pd.read_csv(df_path)
    X1 = np.stack(df.apply(lambda row: combine(row,False), axis = 1).to_numpy())
    y1 = df['output'].to_numpy()
    weight1 = df['weight'].to_numpy()

    X2 = np.stack(df.apply(lambda row: combine(row,True), axis = 1).to_numpy())
    y2 = (1 - df['output']).to_numpy()
    weight2 = df['weight'].to_numpy()

    X = np.concatenate((X1, X2), axis=0)
    y = np.concatenate((y1, y2), axis=0)
    weight = np.concatenate((weight1, weight2), axis=0)

    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
    weight_tensor = torch.tensor(weight, dtype=torch.float32).unsqueeze(1)

    torch.save(X_tensor,"X_"+df_path[:-3]+'pt')
    torch.save(y_tensor,"y_"+df_path[:-3]+'pt')
    torch.save(weight_tensor,"w_"+df_path[:-3]+'pt')
    print("tensor created")
    return X_tensor.to(device), y_tensor.to(device), weight_tensor.to(device)


def start_learning(train_path,test_path,lr,l1_size,l2_size,batch_size,epoch_num):

    train_X, train_y, train_w = get_Tensor(train_path)
    test_X, test_y, test_w = get_Tensor(test_path)
    train_tensor = TensorDataset(train_X, train_y, train_w)
    input_size = test_X.shape[1]
    dataloader = DataLoader(train_tensor, batch_size, shuffle=True)


    if os.path.exists(save_model_name+'.pth'):
        model = torch.load(save_model_name+'.pth')
        print("model loaded")
    else:
        model = ANN(input_size,l1_size,l2_size).to(device)
        print("model created")
    criterion = nn.BCELoss(reduction='none')
    optimizer = torch.optim.Adam(model.parameters(), lr)


    train_loss = {'epoch':[],'Loss':[],'lr':[]}
    test_loss = {'epoch':[],'Test_Loss':[]}
    starting_epoch = 1
    if os.path.exists(save_model_name+'_loss.csv'):
        loss_df = pd.read_csv(save_model_name+'_loss.csv')
        starting_epoch += int(loss_df.iloc[-1]['epoch'])


    for epoch in range(epoch_num):
        for inputs, labels, weights in dataloader:
            inputs, labels, weights = inputs, labels, weights
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss = (loss * weights).sum()/weights.sum()
            loss.backward()
            optimizer.step()

        train_loss['epoch'].append(epoch+starting_epoch)
        train_loss['Loss'].append(loss.item())
        train_loss['lr'].append(lr)
        print(f'Epoch {epoch+starting_epoch}, Loss: {loss.item()}')

        if not (epoch+1) % 10:
            output_test = model(test_X)
            loss_test = criterion(output_test, test_y)
            loss_test = (loss_test * test_w).sum()/test_w.sum()
            test_loss['epoch'].append(epoch+starting_epoch)
            test_loss['Test_Loss'].append(loss_test.item())
            print(f'Epoch {epoch+starting_epoch}, Test_Loss: {loss_test.item()}')



    new_loss_df = pd.merge(pd.DataFrame(train_loss),pd.DataFrame(test_loss),on='epoch',how='outer')

    if os.path.exists(save_model_name+'_loss.csv'):
        loss_df = pd.read_csv(save_model_name+'_loss.csv')
        pd.concat([loss_df,new_loss_df], sort=False).to_csv(save_model_name+'_loss.csv', index=False)
    else:
        new_loss_df.to_csv(save_model_name+'_loss.csv', index=False)
    torch.save(model, save_model_name+'.pth')

def plot_loss(loss_path):
    df = pd.read_csv(loss_path)
    plt.figure(figsize=(10, 5)) 
    plt.scatter(df['epoch'], df['Loss'], label='Training Loss', color='blue', s = 2) 
    plt.scatter(df['epoch'], df['Test_Loss'], label='Test Loss', color='red', s = 5) 

    plt.ylim(0.4, 0.6)
    plt.title('Training and Test Loss vs Epoch')
    plt.ylabel('Loss')
    plt.xticks([epoch for epoch in df['epoch'] if epoch % 100 == 0])
    plt.legend()

    plt.show()


train_path = 'vectorized_train01.csv'
test_path = 'vectorized_test01.csv'
lr = 0.0001
l1_size = 256
l2_size = 128
batch_size = 1024
epoch_num = 100

save_model_name = 'model'+'_'+str(l1_size)+'_'+str(l2_size)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("cuda ready?",torch.cuda.is_available())

start_learning(train_path,test_path,lr,l1_size,l2_size,batch_size,epoch_num)

plot_loss(save_model_name+'_loss.csv')