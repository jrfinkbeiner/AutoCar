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

    MyWorld = SquareWorld(size=SIZE, dynamicObjs=[Car0], online_vizu_bool=True)

    MyWorld.run(num_steps=100)


    # MyWorld.add_dynamic_object(Car0)

    # OrientedRect = OrientedRectangle(orientation=(-1, -1), a=2.0, b=3.0)

    # Pat_OrientedRect = OrientedRect.matplotlib_patch(xy=(0.5 * SIZE[0], 0.5 * SIZE[1]))



    # plot_ground_map(MyWorld=MyWorld) 



def plot_ground_map(MyWorld):
    static_patches, dynamic_patches = MyWorld.obstacle_matplotlib_patches()


    fig, static_ax = plt.subplots(1, sharex=True, sharey=True)
    dynamic_ax = static_ax.twinx().twiny()

    static_ax.patch.set_visible(False)
    static_ax.imshow(MyWorld.ground_map)
    dynamic_ax.set_xlim((0,20))
    dynamic_ax.set_ylim((0,20))
    # static_ax.set_zorder(dynamic_ax.get_zorder()+1)
    print(static_ax.get_zorder())
    print(dynamic_ax.get_zorder())


    # for patch in static_patches:
    #     print(patch)
    #     static_ax.add_patch(patch)

    for patch in dynamic_patches:
        print(patch)
        dynamic_ax.add_patch(patch)

    # fig, static_ax = plt.subplots(1)
    # dynamic_ax = static_ax.twinx().twiny()
    # static_ax.imshow(MyWorld.ground_map)
    # for patch in static_patches:
    #     print(patch)
    #     static_ax.add_patch(patch)


    # for patch in dynamic_patches:
    #     print(patch)
    #     dynamic_ax.add_patch(patch)


    # fig, ax = plt.subplots(1)
    # ax.imshow(MyWorld.ground_map)

    # for patches in [static_patches, dynamic_patches]:
    #     for patch in patches:
    #         print(patch)
    #         ax.add_patch(patch)

    static_ax.grid()


    for patch in dynamic_patches:
        print(patch)
        patch.set_xy([15, 15])
        # patch.angle = 0.0

    plt.show()



if __name__ == '__main__':
    main()