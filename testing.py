import numpy as np
import matplotlib.pyplot as plt


def main():
    x = np.linspace(-1,1,21)
    y = np.arcsin(x)
    print(y)

    fig, ax = plt.subplots(1)
    ax.plot(x, y)
    plt.show()


if __name__ == '__main__':
    main()