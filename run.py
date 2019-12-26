from src.python.world import SquareWorld
from src.python.agent import Agent

import numpy as np
import matplotlib.pyplot as plt


def main():
    MyWorld = SquareWorld(size=(20,20))

    plot_ground_map(MyWorld)


def plot_ground_map(MyWorld):
    plt.figure()
    plt.imshow(MyWorld.ground_map)
    plt.show()


if __name__ == '__main__':
    main()