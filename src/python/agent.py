import numpy as np
import time
import sys
import scipy

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
    

    def _get_part_of_map(self, orientation, ortho_orientation, distance, width): # TODO finish implementation with angles
        # TODO special cases for orientation = [+-1, 0], [0, +-1]
        ground_map = self.World.ground_map
        position = self.position
        scale = self.World.scale
        len_x_ind, len_y_ind = self.World.len_x_ind, self.World.len_y_ind 
        # rear left and rear right positions
        rl = position + ortho_orientation * width * 0.5
        rr = position - ortho_orientation * width * 0.5
        # front left and front right positions
        fl = position + ortho_orientation * width * 0.5 + orientation * distance
        fr = position - ortho_orientation * width * 0.5 + orientation * distance

        # transform corners to indices
        rl_ind = [int(val * scale) for val in rl]
        rr_ind = [int(val * scale) for val in rr]
        fl_ind = [int(val * scale) for val in fl]
        fr_ind = [int(val * scale) for val in fr]

        # determine subsection of interest of ground map
        x_min_ind = min(rl_ind[0], rr_ind[0], fl_ind[0], fr_ind[0])
        x_max_ind = max(rl_ind[0], rr_ind[0], fl_ind[0], fr_ind[0])
        y_min_ind = min(rl_ind[1], rr_ind[1], fl_ind[1], fr_ind[1])
        y_max_ind = max(rl_ind[1], rr_ind[1], fl_ind[1], fr_ind[1])

        if (x_min_ind >= 0) and (x_max_ind <= len_x_ind) and (y_min_ind >= 0) and (y_max_ind <= len_y_ind):
            # if part of map is fully inside ground_map just return part of the map
            coarse_cut_mask = np.ogrid[x_min_ind:x_max_ind, y_min_ind:y_max_ind]
            ground_map_cut = ground_map[tuple(coarse_cut_mask)].copy()
        else:
            # if part of map is partically outside map, pad with BACKGROUND
            ground_map_cut = np.ones((x_max_ind-x_min_ind, y_max_ind-y_min_ind)) * BACKGROUND

            x_min_ind_cut = max(x_min_ind, 0)
            x_max_ind_cut = min(x_max_ind, len_x_ind)
            y_min_ind_cut = max(y_min_ind, 0)
            y_max_ind_cut = min(y_max_ind, len_y_ind)

            # create mask for ground_map
            coarse_cut_mask = np.ogrid[x_min_ind_cut:x_max_ind_cut, y_min_ind_cut:y_max_ind_cut]
            print(coarse_cut_mask[0].shape, coarse_cut_mask[1].shape)
            
            # determine indices to properly shift and cut the ground_map_cut so that shape fits with ground_map[mask]
            zero_shift_x = 0-x_min_ind if x_min_ind < 0 else 0
            zero_shift_y = 0-y_min_ind if y_min_ind < 0 else 0
            len_cut_x = len_x_ind-x_min_ind if x_max_ind > len_x_ind else x_max_ind_cut-x_min_ind
            len_cut_y = len_y_ind-y_min_ind if y_max_ind > len_y_ind else y_max_ind_cut-y_min_ind

            # copy ground_map section to ground_map_cut reagion of interest
            ground_map_cut[zero_shift_x:len_cut_x,zero_shift_y:len_cut_y] = ground_map[tuple(coarse_cut_mask)].copy()

        return ground_map_cut


    def _determine_throttle_and_angle(self, DynamicObj): # TODO MUCH optimization possible, both in comupte performace as in behavior
        current_steering_angle = DynamicObj.steering_angle
        orientation = DynamicObj.Shape.orientation
        orientation_left = DynamicObj.Shape.orthogonal_orientation()
        orientation_right = -orientation_left

        distance_long = 10 # TODO magic value... choose some good value?
        distance_short_front = 5
        distance_short = 3 # TODO magic value... choose some good value?
        width = DynamicObj.Shape.width

        map_front_long = self._get_part_of_map(orientation, orientation_left, distance_long, width)
        map_left_long = self._get_part_of_map(0.5 * (orientation + orientation_left), 0.5 * (-orientation + orientation_left), distance_long, width)
        map_right_long = self._get_part_of_map(0.5 * (orientation + orientation_right), orientation_left, distance_long, width)

        map_front_short = self._get_part_of_map(orientation, orientation_left, distance_short_front, width)
        map_left_short_60 = self._get_part_of_map((orientation + 2 * orientation_left) / 3, (-2 * orientation + orientation_left) / 3, distance_short, width)
        map_right_short_60 = self._get_part_of_map((orientation + 2 * orientation_right) / 3, (2 * orientation + orientation_left) / 3, distance_short, width)
        map_left_short_30 = self._get_part_of_map((2 * orientation + orientation_left) / 3, (-orientation + 2 * orientation_left) / 3, distance_short, width)
        map_right_short_30 = self._get_part_of_map((2 * orientation + orientation_right) / 3, (orientation + 2 * orientation_left) / 3, distance_short, width)

        map_front_immediate = self._get_part_of_map(orientation, orientation_left, 2.5, width)

        throttle = np.tanh(self.optimal_velocity - np.linalg.norm(DynamicObj.velocity))

        if np.all(map_front_long == DRIVABLE):
            # print('front long')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((0.0 - current_steering_angle) * np.pi * 3 / 180) 
            
        elif np.all(map_left_long == DRIVABLE):
            # print('left long')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-45.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_right_long == DRIVABLE):
            # print('right long')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((45.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_left_short_60 == DRIVABLE):
            # print('left short 60')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_right_short_60 == DRIVABLE):
            # print('right short 60')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_left_short_30 == DRIVABLE):
            # print('left short 30')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_right_short_30 == DRIVABLE):
            # print('right short 30')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_front_short == DRIVABLE):
            # print('front short')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((0.0 - current_steering_angle) * np.pi * 3 / 180)
            throttle = np.tanh(self.optimal_velocity * 0.7  - np.linalg.norm(DynamicObj.velocity))
        else:
            print('')
            print('VEHICLE IS STUCK!')
            # sys.exit() # TODO uncomment or do sth different, stop timer, ...

        if not np.all(map_front_immediate == DRIVABLE):
            # print('front immediate')
            # mulipy with 3 to favor large steering wheel changes
            throttle = np.tanh(self.optimal_velocity * 0.1  - np.linalg.norm(DynamicObj.velocity))


        return throttle, steering_wheel_change # TODO implement








from .world import SquareWorld # has to be at the end of module due to circular imports
from .obstacles import DynamicObject