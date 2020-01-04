import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import time

class SquareWorld(object):
    """
    World/Map defined as manly litte squares. 
    Takes
        size : tuple, (len_x, len_y) number of squares for x and y direction
        scale : float, conversion between squares and length scale (metres)
        dynamicObjs : list of DynamicObject, initial dynamic objects 
        staticObjs : list of StaticObject, initial static objects 
    """
    
    def __init__(self, size, scale=1.0, timestep=1.0, dynamicObjs=[], staticObjs=[], online_vizu_bool=True):
        super().__init__()
        self.size = size
        self.len_y, self.len_x = size
        self.scale = scale
        self.timestep = timestep
        
        self.staticObjs = staticObjs
        self.dynamicObjs = dynamicObjs
        self.IDs = []
        self.staticIDs, self.dynamicIDs = self._create_lists_and_assign_IDs()

        self.ground_map = self._create_ground_map()

        self.online_vizu_bool = online_vizu_bool
        if online_vizu_bool:
            self.static_patches = {}
            self.dynamic_patches = {}

            self._update_static_patches()
            self._update_dynamic_patches()

            self.online_vizu = VizuManager(World=self, timestep=timestep, title='World vizu') #TODO


    def run(self, num_steps=None):
        
        if num_steps==None:
            while True:
                self.run_step()
        else:
            assert type(num_steps) == int, f"Expects int, got {type(num_steps)}"
            for _ in tqdm(range(num_steps)):
                self.run_step()

    def run_step(self):
        # # TODO to be del just chekcing
        # print(time.time())
        # self.dynamicObjs[0].Shape.orientation = np.dot(np.array(self.dynamicObjs[0].Shape.orientation), np.array([[np.cos(time.time()), np.sin(time.time())], [-np.sin(time.time()), np.cos(time.time())]]))
        # print(self.dynamicObjs[0].Shape.orientation)
        
        #self.dynamicObjs[0].Shape.update_patch(self.dynamic_patches[0], self.dynamicObjs[0].position)
        self.update()
        print(self.dynamic_patches[0])

    # TODO think about this. Shouldn't it just be a (negative) reward map? Instead of multidim classification map?
    def _create_ground_map(self):
        """
        Creates world, numpy array of size (self.len_x, self.len_y, 2) defining drivable and non drivable space.
        """
        ground_map = np.zeros((self.len_x, self.len_y))
        ground_map = self._define_drivable_space(ground_map) # TODO think
        # TODO possibly other spaces 
        return ground_map

    def _define_drivable_space(self, ground_map):
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
            if not obj.ID in staticIDs:
                staticIDs.append(obj.ID)
                self.IDs.append(obj.ID)
            else:
                raise ValueError("All objects need different IDs. At least two static objects have the same ID.")
            
        for obj in self.dynamicObjs:
            if obj.ID == None:
                unassigned_dynamicObjs.append(obj)
                continue
            if not obj.ID in dynamicIDs:
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


    def _check_and_assign_ID(self):
        # TODO implement
        pass

    def add_dynamic_object(self, obstacle):
        """
        Adds an instance of type DynamicObject to dynamicObjs.
        """
        assert type(obstacle) == DynamicObject, f"Expects instance of type DynamicObject, got {type(obstacle)}."
        # TODO _check_and_assign_ID
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




from .vizualiser import VizuManager
from .obstacles import StaticObject, DynamicObject