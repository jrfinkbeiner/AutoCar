
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import time
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from autocar.python.vizualiser import VizuManager
from autocar.python.obstacles import StaticObject, DynamicObject


class SquareWorld(object):
    """
    World/Map defined as manly litte squares. 
    Takes
        size : tuple, (len_x, len_y) number of squares for x and y direction
        scale : float, squares / meter, conversion between squares and length scale (metres)
        dynamicObjs : list of DynamicObject, initial dynamic objects 
        staticObjs : list of StaticObject, initial static objects 
    """
    
    def __init__(self, size, scale=1.0, timestep=1.0, dynamicObjs=[], staticObjs=[], online_vizu_bool=True):
        super().__init__()
        self.size = size
        self.len_y, self.len_x = size # TODO fucked sth up there....
        self.scale = scale
        self.len_x_ind, self.len_y_ind = int(self.len_x * scale), int(self.len_y * scale)
        self.timestep = timestep
        
        self.staticObjs = staticObjs
        self.dynamicObjs = dynamicObjs
        for dynamicObj in self.dynamicObjs:
            dynamicObj.ControllingAgent.World = self
        self.IDs = []
        self.staticIDs, self.dynamicIDs = self._create_lists_and_assign_IDs()

        self.default_folder = './build/firstSquare'
        self.ground_map = self._create_ground_map()

        self.online_vizu_bool = online_vizu_bool
        if online_vizu_bool:
            self.static_patches = {}
            self.dynamic_patches = {}

            self._update_static_patches()
            self._update_dynamic_patches()

            self.online_vizu = VizuManager(World=self, timestep=timestep, title='World vizu') #TODO


    def save_world(self, folder=None): 
        """
        Saves the current state of the world.
         1. Saves the world instance sa pickle file titled "world.pkl"
         2. Saves the ground map as png titled "map.png"
         3. Saves the static objects as pickle file titles "static.pkl"
         4. Saves the dynamic objects as pickle file titles "dynamic.pkl"
        2.-4. are redundant with 1. but mith be helpful, especially 2. 
        """
        if (folder == None) or (folder == False): # TODO weird shit with false due to functools.partial not beeing implmented in vizualiser
            folder = self.default_folder
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.save_world_instance(folder)
        self.save_map(folder)
        self.save_static(folder)
        self.save_dynamic(folder)


    def save_world_instance(self, folder):
        filename =  os.path.join(folder, 'world.pkl')
        with open(filename, 'wb') as outfile:  # Overwrites any existing file.
            pickle.dump(self, outfile, pickle.HIGHEST_PROTOCOL)

    def save_map(self, folder):
        filename = os.path.join(folder, 'map.npy')
        filename_png = os.path.join(folder, 'map.png')
        plt.imsave(filename_png, self.ground_map)
        np.save(filename, self.ground_map)

    def save_static(self, folder):
        filename =  os.path.join(folder, 'static.pkl')
        with open(filename, 'wb') as outfile:  # Overwrites any existing file.
            pickle.dump(self.staticObjs, outfile, pickle.HIGHEST_PROTOCOL)

    def save_dynamic(self, folder):
        filename =  os.path.join(folder, 'dynamic.pkl')
        with open(filename, 'wb') as outfile:  # Overwrites any existing file.
            pickle.dump(self.staticObjs, outfile, pickle.HIGHEST_PROTOCOL)


    @classmethod
    def load_world(cls, folder):
        filename =  os.path.join(folder, 'world.pkl')
        with open(filename, 'rb') as infile:
            return pickle.load(infile)

    def load_map(self, folder):
        # filename = os.path.join(folder, 'map.png')
        filename = os.path.join(folder, 'map.npy')
        self.ground_map = np.load(filename)

    def load_static(self, folder):
        filename =  os.path.join(folder, 'static.pkl')
        with open(filename, 'rb') as infile:
            loaded_static_objects = pickle.load(infile)
        self.add_static_objects(loaded_static_objects)
        

    def load_dynamic(self, folder):
        filename =  os.path.join(folder, 'dynamic.pkl')
        with open(filename, 'rb') as infile:
            loaded_static_objects = pickle.load(infile)
        self.add_dynamic_objects(loaded_static_objects)


    def run(self, num_steps=None):
        if num_steps==None:
            while True:
                self.run_step()
        else:
            assert type(num_steps) == int, f"Expects int, got {type(num_steps)}"
            for _ in tqdm(range(num_steps)):
                self.run_step()

    def run_step(self):
        print('')
        self.update()
        print(self.dynamic_patches[0])

    # TODO think about this. Shouldn't it just be a (negative) reward map? Instead of multidim classification map?
    def _create_ground_map(self):
        """
        Creates world, numpy array of size scale*(len_y, len_x) defining drivable and non drivable space.
        """
        ground_map = np.zeros((int(self.scale*self.len_y), int(self.scale*self.len_x)), dtype=int)
        ground_map = self._define_drivable_space(ground_map) # TODO think
        # TODO possibly other spaces 
        return ground_map

    def _define_drivable_space(self, ground_map):
        # TODO implement interactive vizu
        """
        Defines areas of drivable space via interactive vizualisation.
        """
        inds_x = int(self.len_x * self.scale)
        inds_y = int(self.len_y * self.scale)
        center_x, center_y = inds_x // 2 , inds_y // 2
        ymask, xmask = np.ogrid[0:inds_y, 0:inds_x]

        outter_rad = int(15 * self.scale)
        inner_rad = int(9 * self.scale)

        square_mask = (xmask-center_x<outter_rad)&(xmask-center_x>-outter_rad)&(ymask-center_y<outter_rad)&(ymask-center_y>-outter_rad)
        square_mask[center_y-inner_rad+1:center_y+inner_rad,center_x-inner_rad+1:center_x+inner_rad] = False

        circle_mask = (xmask-center_x)**2 + (ymask-center_y)**2 <= outter_rad**2
        inner_circle_mask = (xmask-center_x)**2 + (ymask-center_y)**2 <= inner_rad**2
        circle_mask[inner_circle_mask] = False

        ground_map[square_mask] = 1
        return ground_map


    def _create_lists_and_assign_IDs(self):
        staticIDs = []
        dynamicIDs = []
        
        if (len(self.staticObjs) == 0) and (len(self.dynamicObjs) == 0):
            return staticIDs, dynamicIDs

        unassigned_staticObjs = []
        unassigned_dynamicObjs = []

        for obj in self.staticObjs:
            if obj.ID == None:
                unassigned_staticObjs.append(obj)
                continue
            if not obj.ID in self.IDs:
                staticIDs.append(obj.ID)
                self.IDs.append(obj.ID)
            else:
                raise ValueError("All objects need different IDs. At least two static objects have the same ID.")
            
        for obj in self.dynamicObjs:
            if obj.ID == None:
                unassigned_dynamicObjs.append(obj)
                continue
            if not obj.ID in self.IDs:
                dynamicIDs.append(obj.ID)
                self.IDs.append(obj.ID)
            else:
                raise ValueError("All objects need different IDs. Got at least two objects with same ID.")

        missing_IDs = sorted(list(set(range(len(self.staticObjs)+len(self.dynamicObjs))) - set(self.IDs)))
        for unassigned_objs, ID_list in zip([unassigned_staticObjs, unassigned_dynamicObjs], [staticIDs, dynamicIDs]):
            for obj in unassigned_objs:
                
                obj.ID = missing_IDs[0]
                ID_list.append(missing_IDs[0])
                self.IDs.append(missing_IDs[0])
                del missing_IDs[0]

        self.IDs = sorted(self.IDs)
        return staticIDs, dynamicIDs


    def _check_and_assign_ID(self, obj_list, obj_type):

        if obj_type == 'static':
            ID_list = self.staticIDs
        elif obj_type == 'dynamic':
            ID_list = self.dynamicIDs
        else:
            raise ValueError(f"Expects str 'static' or 'dynamic', got {obj_type}")

        unassigned_objs = []
        for instance in obj_list:
            if instance.ID == None:
                unassigned_objs.append(instance)
            elif instance.ID in self.IDs:
                unassigned_objs.append(instance)
            else:
                ID_list.append(instance.ID)
                self.IDs.append(instance.ID)
            
        missing_IDs = sorted(list(set(range(len(self.staticObjs)+len(self.dynamicObjs)+len(obj_list))) - set(self.IDs)))
        
        for instance in unassigned_objs:
            instance.ID = missing_IDs[0]
            self.IDs.append(missing_IDs[0])
            ID_list.append(missing_IDs[0])
            del missing_IDs[0]

        ID_list = sorted(ID_list)
        self.IDs = sorted(self.IDs)


    def add_dynamic_object(self, obstacle, check_ID=True):
        """
        Adds an instance of type DynamicObject to dynamicObjs.
        """
        assert isinstance(obstacle, DynamicObject), f"Expects instance of type DynamicObject, got {type(obstacle)}."
        if check_ID:
            self._check_and_assign_ID([obstacle], 'dynamic')
        self.dynamicObjs.append(obstacle)
        if obstacle.ControllingAgent.World != self:
            obstacle.ControllingAgent.World = self

    def add_dynamic_objects(self, obstacle_list):
        self._check_and_assign_ID(obstacle_list, 'dynamic')
        [self.add_dynamic_object(obstacle=instance, check_ID=False) for instance in obstacle_list]


    def add_static_object(self, obstacle, check_ID=True):
        """
        Adds an instance of type StaticObject to dynamicObjs.
        """
        assert type(obstacle) == StaticObject, f"Expects instance of type StaticObject, got {type(obstacle)}."
        if check_ID:
            self._check_and_assign_ID([obstacle], 'static')
        self.staticObjs.append(obstacle)

    def add_static_objects(self, obstacle_list):
        self._check_and_assign_ID(obstacle_list, 'static')
        [self.add_static_object(obstacle=instance, check_ID=False) for instance in obstacle_list]

    def update(self):
        """
        Updates wolrd given DynamicObstacles Agents and their action/reaction to current Wolrd state. 
        First saves actions to actions list and then executes all actions in actions list that were accumulatet via accumulate_updates at the same time.
        """
        action_list = []
        for instance in self.dynamicObjs:
            assert isinstance(instance, DynamicObject), f"dynamicObjs has to contain only instances of type DynamicObject, got {type(instance)}"
            # TODO
            action = instance.get_action()
            action_list.append((instance, action))

        for (instance, action) in action_list:
            instance.perform_action(action, self.timestep) # self.perform_action(instance, action)

        if self.online_vizu_bool:
            self._update_dynamic_patches()


    # TODO should updates really be accumultaed or should just be updated directly instance for instance? 
    # (otherwise complications with current velocity)

    def accumulate_updates(self, instance):  
        """
        Saves Agents action/reation to world state to list of actions.
            instance : DynamicObject, instnace, e.g. Car
        """
        pass



    def _update_static_patches(self): 
        for instance in self.staticObjs:
            if not (instance.ID in self.static_patches):
                self.static_patches[instance.ID] = instance.return_matplotlib_patch()
            else:
                pass # TODO implement state update of 


    def _update_dynamic_patches(self): 
        for instance in self.dynamicObjs:
            if instance.ID in self.dynamic_patches:
                patch = self.dynamic_patches[instance.ID]
                instance.update_patch(patch)
            else:
                self.dynamic_patches[instance.ID] = instance.return_matplotlib_patch()


    def obstacle_matplotlib_patches(self):
        return self.static_patches.values(), self.dynamic_patches.values()