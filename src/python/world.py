import numpy as np
import matplotlib.pyplot as plt


class SquareWorld(object):
    """
    World/Map defined as manly litte squares. 
    Takes
        size : tuple, (len_x, len_y) number of squares for x and y direction
        scale : float, conversion between squares and length scale (metres)
        dynamicObjs : list of DynamicObject, initial dynamic objects 
        staticObjs : list of StaticObject, initial static objects 
    """
    
    def __init__(self, size, scale=1.0, timestep=1.0, dynamicObjs=[], staticObjs=[]):
        super().__init__()
        self.size = size
        self.len_y, self.len_x = size
        self.scale = scale
        self.timestep = timestep
        self.dynamicObjs = dynamicObjs
        self.staticObjs = staticObjs

        self.static_patches = []
        self.dynamic_patches = []

        self._render_static_patches()
        self._render_dynamic_patches()

        self.ground_map = self.__create_ground_map()



    # TODO think about this. Shouldn't it just be a (negative) reward map? Instead of multidim classification map?
    def __create_ground_map(self):
        """
        Creates world, numpy array of size (self.len_x, self.len_y, 2) defining drivable and non drivable space.
        """
        ground_map = np.zeros((self.len_x, self.len_y))
        ground_map = self.__define_drivable_space(ground_map) # TODO think
        # TODO possibly other spaces 
        return ground_map

    def __define_drivable_space(self, ground_map):
        # TODO implement interactive vizu
        """
        Defines areas of drivable space via interactive vizualisation.
        """
        center_x, center_y = int(self.len_x/2), int(self.len_y/2)
        ymask, xmask = np.ogrid[0:self.len_y, 0:self.len_y]

        outter_rad = 8
        inner_rad = 4

        square_mask = (xmask-center_x<outter_rad)&(xmask-center_x>-outter_rad)&(ymask-center_y<outter_rad)&(ymask-center_y>-outter_rad)
        square_mask[center_y-inner_rad+1:center_y+inner_rad,center_x-inner_rad+1:center_x+inner_rad] = False


        # circle_mask = (xmask-center_x)**2 + (ymask-center_y)**2 <= 5**2
        # print(circle_mask)


        ground_map[square_mask] = 1
        return ground_map

    def add_dynamic_object(self, obstacle):
        """
        Adds an instance of type DynamicObject to dynamicObjs.
        """
        assert type(obstacle) == DynamicObject, f"Expects instance of type DynamicObject, got {type(obstacle)}."
        self.dynamicObjs.append(obstacle)


    def add_static_object(self, obstacle):
        """
        Adds an instance of type StaticObject to dynamicObjs.
        """
        assert type(obstacle) == StaticObject, f"Expects instance of type StaticObject, got {type(obstacle)}."
        self.staticObjs.append(obstacle)


    def update(self):
        """
        Updates wolrd given DynamicObstacles Agents and their action/reaction to current Wolrd state. 
        First saves actions to actions list and then executes all actions in actions list that were accumulatet via accumulate_updates at the same time.
        """
        action_list = []
        for instance in self.dynamicObjs:
            assert type(instance) == DynamicObject, f"dynamicObjs has to contain only instances of type DynamicObject, got {type(instance)}"
            # TODO
            # action = ...
            # action_list.append((obj, action))

        for (instance, action) in action_list:
            self.perform_action(instance, action)

        self._render_dynamic_patches()


    # TODO should updates really be accumultaed or should just be updated directly instance for instance? 
    # (otherwise complications with current velocity)

    def accumulate_updates(self, instance):  
        """
        Saves Agents action/reation to world state to list of actions.
            instance : DynamicObject, instnace, e.g. Car
        """
        pass


    def perform_action(self, instance, action):
        """
        Changes state of world and instance according to action.
        """

        pass


    def _render_static_patches(self): # TODO probably better with some kind of tracking id...
        for instance in self.staticObjs:
            self.static_patches.append(instance.return_matplotlib_patch())

    def _render_dynamic_patches(self): # TODO probably better with some kind of tracking id...
        for instance in self.dynamicObjs:
            self.static_patches.append(instance.return_matplotlib_patch())

    def obstacle_matplotlib_patches(self):
        return self.static_patches, self.dynamic_patches




class Obstacle(object):
    def __init__(self, Shape, initial_position):
        super().__init__()
        self.position = initial_position
        self.Shape = Shape

    def return_matplotlib_patch(self):
        return self.Shape.matplotlib_patch(self.position)


class StaticObject(Obstacle):
    def __init__(self, Shape, initial_position):
        super().__init__(Shape, initial_position)
        assert isinstance(self.Shape, Shape), f"Expects instance that is child class of Shape, got {type(self.Shape)}."


class DynamicObject(Obstacle):
    """
    Dynamic object, inherits form Obstacle.
        Shape : Shape, instance of Shape class determining the shape of the obstacle
        position : list [float posx, float posy], position of the instance on in the wolrd/map
        velocity : list [float vx, float vy], velocity with which the instance is displaced
        acceleration : list [float ax, float ay], acceleration of the instance
        ControllingAgent : Agent, agent that takes world and instance state and chooses action to take
    """
    def __init__(self, Shape, initial_position, initial_velocity, initial_acceleration, ControllingAgent):
        super().__init__(Shape, initial_position)
        assert isinstance(self.Shape, OrientedShape), f"Expects instance that is child class of OrientedShapes, got {type(self.Shape)}."
        self.acceleration = initial_acceleration
        self.velocity = initial_velocity
        self.ControllingAgent = ControllingAgent

    def update_state(self, timestep):
        self.update_acceleration()
        self.update_velocity(timestep)
        self.update_position(timestep)

    def update_position(self, timestep):
        self.position += self.velocity * timestep

    def update_velocity(self, timestep):
        self.velocity = self.velocity # TODO

    def update_acceleration(self):
        self.acceleration = self.acceleration # TODO


from .shapes import *

    