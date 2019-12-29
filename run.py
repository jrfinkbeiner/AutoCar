import numpy as np
import matplotlib.pyplot as plt

from src.python.world import SquareWorld, DynamicObject
from src.python.agent import Agent
from src.python.shapes import OrientedRectangle


def main():
    SIZE = (20,20)



    init_pos = [0.5 * SIZE[0], 0.5 * SIZE[1]]

    OrientedRect0 = OrientedRectangle(orientation=[-1, -1], a=2.0, b=3.0)

    Car0 = DynamicObject(Shape=OrientedRect0, 
                        initial_position=init_pos, 
                        initial_velocity=[0.0, 0.0],
                        initial_acceleration=[0.0, 0.0],
                        ControllingAgent=Agent())

    MyWorld = SquareWorld(size=SIZE, dynamicObjs=[Car0])



    # MyWorld.add_dynamic_object(Car0)

    # OrientedRect = OrientedRectangle(orientation=(-1, -1), a=2.0, b=3.0)

    # Pat_OrientedRect = OrientedRect.matplotlib_patch(xy=(0.5 * SIZE[0], 0.5 * SIZE[1]))





    plot_ground_map(MyWorld=MyWorld) #


def plot_ground_map(MyWorld, patches=[]):
    static_patches, dynamic_patches = MyWorld.obstacle_matplotlib_patches()
    fig, ax = plt.subplots(1)
    ax.imshow(MyWorld.ground_map)

    for patches in [static_patches, dynamic_patches]:
        for patch in patches:
            print(patch)
            ax.add_patch(patch)
    plt.grid()
    plt.show()


if __name__ == '__main__':
    main()