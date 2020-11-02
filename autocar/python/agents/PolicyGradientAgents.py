import numpy as np
from abc import ABC

from agent import RayAgent

# TODO not implemented yet

class PolicyGradientAgent(ABC):
    def __init__(self):
        super().__init__()

    @property
    def module(self):
        return self._module

    def set_module(self, module):
        self._module = module

    @abstractmethod
    def get_action(self, state_tensor):
        raise NotImplementedError


class PGRayAgent(PolicyGradientAgent, RayAgent):

    def __init__(self): #, state_scale: torch.Tensor, state_shift: torch.Tensor):
        super().__init__()
        # self.state_scale = state_scale
        # self.state_shift = state_shift


    def get_action(self, state_tensor: torch.Tensor):
        return self._module(state_tensor)


    def _get_throttle_and_angle(self, DynamicObj, distances):
        
        current_steering_angle = DynamicObj.steering_angle
        velocity = DynamicObj.velocity
        orientation = DynamicObj.Shape.orientation

        state_tensor = torch.Tensor([velocity, orientation, current_steering_angle, *distances])
        # dyn_state = torch.Tensor([velocity, orientation, current_steering_angle]).unsqueeze()
        # proccessed_dyn_state = dyn_state*self.state_scale + self.state_shift
        # distance_tensor = torch.Tensor(distances)
        # state_tensor = torch.cat((proccessed_dyn_state, distance_tensor), 0).unsqueeze()
        
        action_tensor = self.get_action(state_tensor)
        return action_tensor[0,0], action_tensor[0,1]



        

