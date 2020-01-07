import numpy as np
import time

BACKGROUND = 0
DRIVABLE = 1

class Agent(object):
    """
    Agent that acts in World.
        initial_position : tuple of floates, intitail position in World in metres

    """
    def __init__(self, World=None, initial_position=None):
        super().__init__()
        self.current_position = initial_position
        self.World = World
        self.observable_world = None

    def set_world(self, World):
        assert isinstance(World, SquareWorld), f"Expects instance of type SquareWorld, got {type(World)}"
        self.World

    def _observe_world(self):
        """
        Determines the part of the world that is visible to the agent.
        """
        
        raise NotImplementedError

    def determine_action(self, DynamicObj):
        """
        Determines the action the Agent takes given the current state of the world and its position in it.
        """
        assert isinstance(self.World, SquareWorld), f"World has to be set before Agent can determine actions."
        self._observe_world()
        self.position = DynamicObj.position

        raise NotImplementedError





class SimpleAgent(Agent):
    def __init__(self, World=None, initial_position=None):
        super().__init__(World, initial_position)
        self.optimal_velocity = 5 # TODO set optimal velocity, later possibly by adjusting to world state

    def _observe_world(self):
        assert isinstance(self.World, SquareWorld), f"Expects instance of type SquareWorld, got {type(self.World)}"
        self.observable_world = self.World # TODO reduce to imperfect world, not whole world is known at each timestep

    def determine_action(self, DynamicObj):
        # TODO maybe specify exact dynamic object in agent subclasses
        assert isinstance(DynamicObj, DynamicObject), f"Expects instance of type DynamicObject, got {type(DynamicObj)}" 
        self._observe_world()
        self.position = DynamicObj.position
        action = {}


        throttle, steering_wheel_change = self._determine_throttle_and_angle(DynamicObj) # better: absolute acc val + steering wheel angle


        action['throttle'] = throttle
        action['steering_wheel_change'] = steering_wheel_change
        return action
    

    def _get_part_of_map(self, orientation, distance, witdh):
        ground_map = self.World.ground_map
        position = self.position
        scale = self.World.scale

        




        mask = ground_map==ground_map


        return ground_map[mask]




    def _determine_throttle_and_angle(self, DynamicObj):
        current_steering_angle = DynamicObj.steering_angle
        orientation = DynamicObj.Shape.orientation
        orientation_left = DynamicObj.orthogonal_orientation()
        orientation_right = -orientation_left

        distance_long = 9 # TODO magic value... choose some good value?
        distance_short = 3 # TODO magic value... choose some good value?

        map_front_long = _get_part_of_map(orientation, distance_long)
        map_left_long = _get_part_of_map(0.5 * (orientation + orientation_left), distance_long)
        map_right_long = _get_part_of_map(0.5 * (orientation + orientation_right), distance_long)

        map_front_short = _get_part_of_map(orientation, distance_short)
        map_left_short = _get_part_of_map((2 * orientation + orientation_left) / 3, distance_short)
        map_right_short = _get_part_of_map((2 * orientation + orientation_right)  / 3, distance_short)



        throttle = np.tanh(self.optimal_velocity - DynamicObj.velocity)


        if np.all(map_front_long == DRIVABLE):
            steering_wheel_change = np.tanh((0.0 - current_steering_angle) * np.pi * 3 / 180) 
            
        elif np.all(map_left_long == DRIVABLE):
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-45.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_right_long == DRIVABLE):
            steering_wheel_change = np.tanh((45.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_left_short == DRIVABLE):
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle *= 0.5

        elif np.all(map_right_short == DRIVABLE):
            steering_wheel_change = np.tanh((60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle *= 0.5


        return throttle, steering_wheel_change # TODO implement











from .world import SquareWorld # has to be at the end of module due to circular imports
from .obstacles import DynamicObject