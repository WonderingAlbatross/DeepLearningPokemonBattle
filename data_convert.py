import pandas as pd


df = pd.read_csv("data.csv",header=0)
df.to_parquet("data.parquet", compression=None)