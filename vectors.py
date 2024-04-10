import pandas as pd
import numpy as np

data = pd.DataFrame(columns = ['x5', 'y5'])
existing = pd.read_csv('William_Denny_Runs.csv')
print(existing)

data = pd.concat([data, pd.read_csv('points.txt', delimiter=',', header=None, names=['x5', 'y5'])], ignore_index=True)
existing = pd.concat([existing, data], ignore_index=False, axis=1)
print(data)

#test = pd.concat([existing, data], ignore_index=False, axis=1)
#print(test)

existing.to_csv('William_Denny_Runs.csv', index=False)