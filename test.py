import numpy as np


a = {}
for i in range(122):
    a[str(i)] = str(i + 10)


splits = np.array_split(list(a.keys()), 6)
print(len(a))