import numpy as np
import matplotlib.pyplot as plt

from src.python.world import SquareWorld
from src.python.obstacles import TwoDOFObject
from src.python.agents.agent import SimpleAgent, RayAgent
from src.python.shapes import OrientedRectangle


def main():
    SIZE = (40, 40)


    init_pos = [0.2 * SIZE[0], 0.5 * SIZE[1]]
    init_pos1 = [0.8 * SIZE[0], 0.5 * SIZE[1]]

    OrientedRect0 = OrientedRectangle(orientation=[0., 1], width=2.0, length=3.0)
    OrientedRect1 = OrientedRectangle(orientation=[0.05, -1], width=2.0, length=3.0)


    Car0 = TwoDOFObject(Shape=OrientedRect0, 
                        initial_position=init_pos, 
                        initial_velocity=[0.0, 5.0],
                        initial_acceleration=[0.0, 0.0],
                        initial_steering_angle=-60.0, 
                        ControllingAgent=RayAgent(num_rays=5))

    Car1 = TwoDOFObject(Shape=OrientedRect1, 
                        initial_position=init_pos1, 
                        initial_velocity=[0.0, -5.0],
                        initial_acceleration=[0.0, 0.0],
                        initial_steering_angle=-60.0, 
                        ControllingAgent=SimpleAgent())

    MyWorld = SquareWorld(size=SIZE, scale=20.0, timestep=0.1, dynamicObjs=[Car1], online_vizu_bool=True)

    # MyWorld.run(num_steps=100)


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