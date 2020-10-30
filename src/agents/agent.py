import numpy as np
import time
import sys
import scipy
import pprint

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


    @staticmethod
    def line_connection(x, point_left, point_right, xmin, ymin):
        m = (point_right[1] - point_left[1]) / (point_right[0] - point_left[0])
        c = point_left[1] - ymin
        x0 = point_left[0] - xmin
        # print(point_left)
        # print(point_right)
        # print('m, c, x0')
        # print(m, c, x0)
        # print(x-x0)
        return (x-x0) * m + c 



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

        throttle, steering_wheel_change = self._determine_throttle_and_angle(DynamicObj) # better: absolute acc val + steering wheel angle ?

        action['throttle'] = throttle
        action['steering_wheel_change'] = steering_wheel_change
        return action
    
    def _get_part_of_map(self, orientation, ortho_orientation, distance, width): 
        ground_map = self.World.ground_map
        position = self.position
        scale = self.World.scale
        num_x_ind, num_y_ind = self.World.len_x_ind-1, self.World.len_y_ind-1 # -1 to go from len to max ind
        # rear left and rear right positions
        rl = position + ortho_orientation * width * 0.5
        rr = position - ortho_orientation * width * 0.5
        # front left and front right positions
        fl = position + ortho_orientation * width * 0.5 + orientation * distance
        fr = position - ortho_orientation * width * 0.5 + orientation * distance

        corners = np.array([rl, rr, fl, fr])
        # calculate coreners in indices of ground_map
        corners_ind = (corners * scale).astype(int)

        # determine subsection of interest of ground map
        x_min_ind = np.min(corners_ind[:,0])
        x_max_ind = np.max(corners_ind[:,0])
        y_min_ind = np.min(corners_ind[:,1])
        y_max_ind = np.max(corners_ind[:,1])

        if (x_min_ind >= 0) and (x_max_ind <= num_x_ind) and (y_min_ind >= 0) and (y_max_ind <= num_y_ind):
            # if part of map is fully inside ground_map just return part of the map
            coarse_cut_mask = np.ogrid[y_min_ind:y_max_ind+1, x_min_ind:x_max_ind+1]
            ground_map_cut = ground_map[tuple(coarse_cut_mask)].copy()

            x_min_ind_cut = x_min_ind
            x_max_ind_cut = x_max_ind
            y_min_ind_cut = y_min_ind
            y_max_ind_cut = y_max_ind

        else:
            # if part of map is partically outside map, pad with BACKGROUND
            ground_map_cut = np.ones((y_max_ind-y_min_ind+1, x_max_ind-x_min_ind+1)) * BACKGROUND

            x_min_ind_cut = max(x_min_ind, 0)
            x_max_ind_cut = min(x_max_ind, num_x_ind)
            y_min_ind_cut = max(y_min_ind, 0)
            y_max_ind_cut = min(y_max_ind, num_y_ind)

            # create mask for ground_map
            coarse_cut_mask = np.ogrid[y_min_ind_cut:y_max_ind_cut+1, x_min_ind_cut:x_max_ind_cut+1]
            
            # determine indices to properly shift and cut the ground_map_cut so that shape fits with ground_map[mask]
            zero_shift_x = 0-x_min_ind if x_min_ind < 0 else 0
            zero_shift_y = 0-y_min_ind if y_min_ind < 0 else 0
            len_cut_x = num_x_ind-x_min_ind if x_max_ind > num_x_ind else x_max_ind_cut-x_min_ind
            len_cut_y = num_y_ind-y_min_ind if y_max_ind > num_y_ind else y_max_ind_cut-y_min_ind

            # copy ground_map section to ground_map_cut reagion of interest
            ground_map_cut[zero_shift_y:len_cut_y+1,zero_shift_x:len_cut_x+1] = ground_map[tuple(coarse_cut_mask)].copy()
            # print(ground_map_cut)

        if list(orientation) in [[1.,0.], [-1.,0.], [0.,1.], [0.,-1.]]:
            return ground_map_cut # TODO or is sth. broken already before that for those orientations ?
        else:
            corner_xmin = corners[np.argmin(corners[:,0]),:]
            corner_xmax = corners[np.argmax(corners[:,0]),:]
            corner_ymin = corners[np.argmin(corners[:,1]),:]
            corner_ymax = corners[np.argmax(corners[:,1]),:]

            ymask, xmask = np.ogrid[0:ground_map_cut.shape[0], 0:ground_map_cut.shape[1]]

            bot_right_mask = self.line_connection(xmask/scale, corner_ymax, corner_xmax, corner_xmin[0], corner_ymin[1]) < ymask/scale
            bot_left_mask = self.line_connection(xmask/scale, corner_xmin, corner_ymax, corner_xmin[0], corner_ymin[1]) < ymask/scale
            top_right_mask = self.line_connection(xmask/scale, corner_ymin, corner_xmax, corner_xmin[0], corner_ymin[1]) > ymask/scale
            top_left_mask = self.line_connection(xmask/scale, corner_xmin, corner_ymin, corner_xmin[0], corner_ymin[1]) > ymask/scale

            # plug the four corner maks together to one mask
            corner_masks = [bot_right_mask, bot_left_mask, top_right_mask, top_left_mask]
            mask = np.ones(ground_map_cut.shape, dtype=bool)
            for corner_mask in corner_masks:
                mask[corner_mask] = False

            return ground_map_cut[mask]


    def _determine_throttle_and_angle(self, DynamicObj): # TODO MUCH optimization possible, both in comupte performace as in behavior
        current_steering_angle = DynamicObj.steering_angle
        orientation = DynamicObj.Shape.orientation
        orientation_left = DynamicObj.Shape.orthogonal_orientation()
        orientation_right = -orientation_left

        distance_long = 10 # TODO magic value... choose some good value?
        distance_short_front = 5
        distance_short = 3 # TODO magic value... choose some good value?
        width = DynamicObj.Shape.width

        sqrt1div37 = np.sqrt(1/37)
        sqrt1div2 = np.sqrt(0.5)
        map_front_long = self._get_part_of_map(orientation, orientation_left, distance_long, width)
        map_left_long = self._get_part_of_map(sqrt1div2 * (orientation + orientation_left), sqrt1div2 * (-orientation + orientation_left), distance_long, width)
        map_right_long = self._get_part_of_map(sqrt1div2 * (orientation + orientation_right), sqrt1div2 * (orientation + orientation_left), distance_long, width)
        map_left_long_15 = self._get_part_of_map(sqrt1div37 * (6 * orientation + orientation_left), sqrt1div37 * (-orientation + 6 * orientation_left), distance_long, width)
        map_right_long_15 = self._get_part_of_map(sqrt1div37 * (6 * orientation + orientation_right), sqrt1div37 * (orientation + 6 * orientation_left), distance_long, width)

        sqrt1div5 = np.sqrt(1/5)
        map_front_short = self._get_part_of_map(orientation, orientation_left, distance_short_front, width)
        map_left_short_60 = self._get_part_of_map((orientation + 2 * orientation_left) * sqrt1div5, (-2 * orientation + orientation_left) * sqrt1div5, distance_short, width)
        map_right_short_60 = self._get_part_of_map((orientation + 2 * orientation_right) * sqrt1div5, (2 * orientation + orientation_left) * sqrt1div5, distance_short, width)
        map_left_short_30 = self._get_part_of_map((2 * orientation + orientation_left) * sqrt1div5, (-orientation + 2 * orientation_left) * sqrt1div5, distance_short, width)
        map_right_short_30 = self._get_part_of_map((2 * orientation + orientation_right) * sqrt1div5, (orientation + 2 * orientation_left) * sqrt1div5, distance_short, width)

        map_front_immediate = self._get_part_of_map(orientation, orientation_left, 2.5, width)

        throttle = np.tanh(self.optimal_velocity - np.linalg.norm(DynamicObj.velocity))

        if np.all(map_front_long == DRIVABLE):
            print('front long')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((0.0 - current_steering_angle) * np.pi * 3 / 180) 
            
        elif np.all(map_left_long == DRIVABLE):
            print('left long')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-45.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_right_long == DRIVABLE):
            print('right long')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((45.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_left_long_15 == DRIVABLE):
            print('left long 15')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-15.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_right_long_15 == DRIVABLE):
            print('right long 15')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((15.0 - current_steering_angle) * np.pi * 3 / 180) 

        elif np.all(map_left_short_30 == DRIVABLE):
            print('left short 30')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_right_short_30 == DRIVABLE):
            print('right short 30')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_left_short_60 == DRIVABLE):
            print('left short 60')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((-60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_right_short_60 == DRIVABLE):
            print('right short 60')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((60.0 - current_steering_angle) * np.pi * 3 / 180) 
            throttle = np.tanh(self.optimal_velocity * 0.5  - np.linalg.norm(DynamicObj.velocity))

        elif np.all(map_front_short == DRIVABLE):
            print('front short')
            # mulipy with 3 to favor large steering wheel changes
            steering_wheel_change = np.tanh((0.0 - current_steering_angle) * np.pi * 3 / 180)
            throttle = np.tanh(self.optimal_velocity * 0.7  - np.linalg.norm(DynamicObj.velocity))
        else:
            print('')
            print('VEHICLE IS STUCK!')
            # sys.exit() # TODO uncomment or do sth different, stop timer, ...

        if not np.all(map_front_immediate == DRIVABLE):
            print('front immediate')
            # mulipy with 3 to favor large steering wheel changes
            throttle = np.tanh(self.optimal_velocity * 0.1 - np.linalg.norm(DynamicObj.velocity))


        return throttle, steering_wheel_change




class RayAgent(Agent):
    def __init__(self, num_rays, max_distance=50, World=None, initial_position=None):
        super().__init__(World, initial_position)
        self.optimal_velocity = 5 # TODO set optimal velocity, later possibly by adjusting to world state
        self.num_rays = num_rays
        self.max_distance = max_distance

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
    


    def _get_drivable_distance(self, orientation, max_distance): 
        ground_map = self.World.ground_map
        position = self.position
        scale = self.World.scale
        # len_x, len_y = self.World.len_x, self.World.len_y
        len_x_ind, len_y_ind = self.World.len_x_ind, self.World.len_y_ind
        distance_factor = 1/np.max(np.abs(orientation))

        # rear left and rear right positions
        rear = position
        front = position + orientation * max_distance

        corners = np.array([rear, front])
        # calculate coreners in indices of ground_map
        corners_ind = (corners * scale).astype(int)

        # determine subsection of interest of ground map
        x_min_arg = np.argmin(corners[:,0])
        x_max_arg = 1-x_min_arg
        y_min_arg = np.argmin(corners[:,1])
        y_max_arg = 1-y_min_arg

        # x_min = corners_ind[x_min_arg, 0]
        # x_max = corners_ind[x_max_arg, 0]
        # y_min = corners_ind[y_min_arg, 1]
        # y_max = corners_ind[y_max_arg, 1]

        x_min_ind = corners_ind[x_min_arg, 0]
        x_max_ind = corners_ind[x_max_arg, 0]
        y_min_ind = corners_ind[y_min_arg, 1]
        y_max_ind = corners_ind[y_max_arg, 1]

        # calculate number of pixels 
        num_steps = max(y_max_ind-y_min_ind, x_max_ind-x_min_ind)

        # calculate positions for corresponding squares/pixels
        positions = np.linspace(0,1,num_steps).reshape(-1,1) * orientation.reshape(1,2) * max_distance + position
        pos_inds = (positions * scale).astype(int)

        # cut out parts outside map
        cut_mask_x = np.logical_and((-1 < pos_inds[:,0]), (pos_inds[:,0] < len_x_ind))
        cut_mask_y = np.logical_and((-1 < pos_inds[:,1]), (pos_inds[:,1] < len_y_ind))
        cut_mask = np.logical_and(cut_mask_x, cut_mask_y)
        pos_inds_cut = pos_inds[cut_mask,:]

        # determine squares/pixles of interest and of those the DRIVABLE ones
        ground_map_cut = ground_map[pos_inds_cut[:,1], pos_inds_cut[:,0]]
        non_drivable_inds = np.argwhere(ground_map_cut != DRIVABLE)
        # drivable_inds = np.argwhere(ground_map_cut == DRIVABLE)
        
        # calculate distance from number of drivable pixels
        distance = max_distance if len(non_drivable_inds)==0 else abs(non_drivable_inds[0][0]) * distance_factor/ scale
        # distance = 0.0 if len(drivable_inds)==len(ground_map_cut) else drivable_inds[0][0] * distance_factor/ scale

        # print('distance')
        # print(orientation)
        # print(distance)
        # print(np.linalg.norm(positions[-1]-positions[0]))
        # print(distance_factor)

        return distance


    def _determine_throttle_and_angle(self, DynamicObj): # TODO MUCH optimization possible, both in comupte performace as in behavior
        orientation = DynamicObj.Shape.orientation

        orientation_angle = DynamicObj.Shape.calc_angle_from_orientation(orientation)
         
        # TODO at this point only forward pointing rays. Could be changed... (then num rays schould be even to prevent double backwards ponting ray)
        ray_angles =  np.linspace(-1,1,self.num_rays)*np.pi/2 + orientation_angle 
        ray_orientations = list(map(DynamicObj.Shape.calc_orientation_from_angle, ray_angles))
        max_distances = np.ones((self.num_rays))*self.max_distance 

        distances = list(map(self._get_drivable_distance, ray_orientations, max_distances))
                
        # print('ray_angles')
        # print(ray_angles)
        # print('ray_orientations')
        # print(np.array(ray_orientations))
        # print('distances')
        # print(distances)
        throttle, steering_wheel_change = self._get_throttle_and_angle(DynamicObj, distances)

        return throttle, steering_wheel_change


    def  _get_throttle_and_angle(self, DynamicObj, distances):
        raise NotImplementedError





from .world import SquareWorld # has to be at the end of module due to circular imports
from .obstacles import DynamicObject