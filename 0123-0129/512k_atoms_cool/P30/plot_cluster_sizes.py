import numpy as np
import matplotlib.pyplot as plt

for i in [1, 2, 3]:
    data = np.loadtxt(f"{i}_cluster_sizes.txt")
    plt.plot(data[:, 0], data[:, 1])

plt.xscale("log")
#plt.yscale("log")
plt.show()
