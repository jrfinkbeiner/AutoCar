import numpy as np
import matplotlib.pyplot as plt


x = np.linspace(-1,1,21)
y = np.arcsin(x)
print(y)




fig, ax = plt.subplots(1)
ax.plot(x, y)
plt.show()
