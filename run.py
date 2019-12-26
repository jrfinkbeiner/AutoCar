import numpy as np
import matplotlib.pyplot as plt

from src.python.world import SquareWorld
from src.python.agent import Agent
from src.python.shapes import OrientedRectangle


def main():
    SIZE = (20,20)
    MyWorld = SquareWorld(size=SIZE)


    OrientedRect = OrientedRectangle(orientation=(-1, -1), a=2.0, b=3.0)

    Pat_OrientedRect = OrientedRect.matplotlib_patch(xy=(0.5 * SIZE[0], 0.5 * SIZE[1]))


    plot_ground_map(MyWorld=MyWorld, patches=[Pat_OrientedRect])


def plot_ground_map(MyWorld, patches=[]):
    fig, ax = plt.subplots(1)
    ax.imshow(MyWorld.ground_map)
    for patch in patches:
        ax.add_patch(patch)
    plt.grid()
    plt.show()


if __name__ == '__main__':
    main()