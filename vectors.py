import pandas as pd
import numpy as np

data = pd.DataFrame(columns = ['x', 'y'])
data = pd.concat([data, pd.read_csv('points.txt', delimiter=',', header=None, names=['x', 'y'])], ignore_index=True)

print(data)

data.to_csv('Run1.csv', index=False)