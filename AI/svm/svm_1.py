import pandas as pd

df = pd.read_csv('iris.csv')
df = df.drop(['Id'], axis=1)
target = df['Species']
s = set()
for val in target:
    s.add(val)
s = list(s)
rows = list(range(100,150))
df = df.drop(df.index[rows])