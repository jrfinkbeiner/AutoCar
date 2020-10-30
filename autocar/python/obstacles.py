import numpy as np
from scipy.integrate import RK23, RK45
import pprint
import sys # TODO to be del

from autocar.python.shapes import *

class Obstacle(object):
    def __init__(self, Shape, initial_position, ID=None):
        super().__init__()
        self.Shape = Shape
        self.position = np.asarray(initial_position)
        self.ID = ID

    def return_matplotlib_patch(self):
        return self.Shape.matplotlib_patch(self.position)


class StaticObject(Obstacle):
    def __init__(self, Shape, initial_position, ID=None):
        super().__init__(Shape, initial_position, ID)
        assert isinstance(self.Shape, Shape), f"Expects instance that is child class of Shape, got {type(self.Shape)}."

    def update_patch(self):
        self.Shape.update_patch() # TODO implement


class DynamicObject(Obstacle):
    """
    Dynamic object, inherits form Obstacle.
        Shape : Shape, instance of Shape class determining the shape of the obstacle
        ID : int, ID for tracking/referencing
        position : list [float posx, float posy], position of the instance on in the wolrd/map
        velocity : list [float vx, float vy], velocity with which the instance is displaced
        acceleration : list [float ax, float ay], acceleration of the instance
        ControllingAgent : Agent, agent that takes world and instance state and chooses action to take
    """
    def __init__(self, Shape, ControllingAgent, initial_position, initial_velocity, initial_acceleration, initial_steering_angle, ID=None):
        super().__init__(Shape, initial_position, ID)
        assert isinstance(self.Shape, OrientedShape), f"Expects instance that is child class of OrientedShapes, got {type(self.Shape)}."
        self.acceleration = np.asarray(initial_acceleration)
        self.velocity = np.asarray(initial_velocity)
        self.ControllingAgent = ControllingAgent
        self.steering_angle = initial_steering_angle
           

    def get_action(self):
        return self.ControllingAgent.determine_action(self)


    def perform_action(self, action, timestep):
        """
        Changes state of instance according to action.
        """
        self.update_state(action, timestep)


    def steering_wheel_to_angle(self, steering_wheel_change): # TODO finetune
        """
        Transforms steering_wheel_change to change in steering_angle
            [-1, 1] -> [-15 to 15] , 15 degrees is the maximum change of the steering wheel 
        """
        self.steering_angle += steering_wheel_change * 15
        if self.steering_angle < -60:
            self.steering_angle = -60
        if self.steering_angle > 60:
            self.steering_angle = 60

    def _throttle_and_angle_to_acceleration(self, throttle, timestep): # TODO finetune
        """
        Transform action["throttle"] to accelertation taking orientation into account
            [-1, 1] -> ([-6.5 to 6.5], [-6.5 to 6.5]) 
        """
        turn_radius = self.Shape.length / np.sin(self.steering_angle * np.pi / 180)

        angle_change = 2 * np.pi * np.linalg.norm(self.velocity) * timestep / (2 * np.pi * turn_radius)
        angle = self.Shape.calc_rot_angle() + angle_change # TODO don't just add steering angle

        orientation = self.Shape.calc_orientation_from_angle(angle) 
        self.Shape.orientation = orientation 
        orthogonal_orientation = self.Shape.orthogonal_orientation()

        self.acceleration = orientation * throttle * 6.5 - orthogonal_orientation * np.linalg.norm(self.velocity)**2 / turn_radius


    def update_state(self, action, timestep): # TODO pyhscally correct update cycle...?
        # TODO implement steering angle, longitudinal and lateral forces, slip angle...
        self._update_acceleration(action, timestep)
        self._update_position(timestep)
        self._update_velocity(timestep)

        print('self.position')
        print(self.position)
        print('self.velocity')
        print(self.velocity)
        print(np.linalg.norm(self.velocity))
        print('DONE update')

    def _update_position(self, timestep):
        self.position += 0.5 * self.acceleration * timestep**2 + self.velocity * timestep

    def _update_velocity(self, timestep):
        self.velocity += self.acceleration * timestep # TODO 

    def _update_acceleration(self, action, timestep):
        throttle = action['throttle']
        stearing_wheel_change = action['steering_wheel_change']
        pprint.pprint(action)

        self.steering_wheel_to_angle(stearing_wheel_change)
        self._throttle_and_angle_to_acceleration(throttle, timestep)
        print('DONE acc')

    def update_patch(self, patch): # TODO really like this or just give the object/Shape the patch itself?
        self.Shape.update_patch(patch, self.position) # TODO needs orientation update



class TwoDOFObject(DynamicObject):
    """
    Dynamic object, inherits form Obstacle.
        Shape : Shape, instance of Shape class determining the shape of the obstacle
        ID : int, ID for tracking/referencing
        position : list [float posx, float posy], position of the instance on in the wolrd/map
        velocity : list [float vx, float vy], velocity with which the instance is displaced
        acceleration : list [float ax, float ay], acceleration of the instance
        ControllingAgent : Agent, agent that takes world and instance state and chooses action to take
    """
    def __init__(self, Shape, ControllingAgent, initial_position, initial_velocity, initial_acceleration, initial_steering_angle, inital_ID=None):
        super().__init__(Shape, ControllingAgent, initial_position, initial_velocity, initial_acceleration, initial_steering_angle, inital_ID)
   

    def steering_wheel_to_angle(self, steering_wheel_change): # TODO finetune
        """
        Transforms steering_wheel_change to change in steering_angle
            [-1, 1] -> [-15 to 15] , 15 degrees is the maximum change of the steering wheel 
        """
        self.steering_angle += steering_wheel_change * 60 # TODO figure this out!!! maybe including timestep...
        if self.steering_angle < -60:
            self.steering_angle = -60
        if self.steering_angle > 60:
            self.steering_angle = 60

    def _throttle_and_angle_to_acceleration(self, throttle, timestep): # TODO finetune
        """
        Transform action["throttle"] to accelertation taking orientation into account
            [-1, 1] -> ([-6.5 to 6.5], [-6.5 to 6.5]) 
        """
        turn_radius = self.Shape.length / np.sin(self.steering_angle * np.pi / 180)

        angle_change = 2 * np.pi * np.linalg.norm(self.velocity) * timestep / (2 * np.pi * turn_radius)
        angle = self.Shape.calc_rot_angle() + angle_change 

        orientation = self.Shape.calc_orientation_from_angle(angle) 
        self.Shape.orientation = orientation 
        orthogonal_orientation = self.Shape.orthogonal_orientation()

        self.acceleration = orientation * throttle * 6.5 - orthogonal_orientation * np.linalg.norm(self.velocity)**2 / turn_radius


    def update_state(self, action, timestep): # TODO pyhscally correct update cycle...?
        # TODO implement steering angle, longitudinal and lateral forces, slip angle...
        self._update_acceleration(action, timestep)
        self._update_position(timestep)
        self._update_velocity(timestep)

        print('self.position')
        print(self.position)
        print('self.velocity')
        print(self.velocity)
        print(np.linalg.norm(self.velocity))
        print('DONE update')

    def _update_position(self, timestep):
        self.position += 0.5 * self.acceleration * timestep**2 + self.velocity * timestep

    def _update_velocity(self, timestep):
        self.velocity += self.acceleration * timestep 

    def _update_acceleration(self, action, timestep):
        throttle = action['throttle']
        stearing_wheel_change = action['steering_wheel_change']

        pprint.pprint(action)
        print(f"steering_angle = {self.steering_angle}")
        self.steering_wheel_to_angle(stearing_wheel_change)
        self._throttle_and_angle_to_acceleration(throttle, timestep)
        print('DONE acc')

    def update_patch(self, patch): # TODO really like this or just give the object/Shape the patch itself?
        self.Shape.update_patch(patch, self.position) # TODO needs orientation update



class ThreeDOFObject(DynamicObject):
    # TODO possibly write unit-test comparing to paper (Smith Vehicle Response) to guarentee correctness of model
    def __init__(self, Shape, ControllingAgent, initial_position, initial_velocity, initial_acceleration, initial_orientation, inital_steering_angle, ID=None):
        super().__init__(Shape, ControllingAgent, initial_position, initial_velocity, initial_acceleration, ID)
        self.orientation = np.asarray(initial_orientation) # TODO already in shape
        self.steering_angle = inital_steering_angle

        # Vehicle Parameter Used for Simulation Study used in paper
        self.yaw_inertia = 2380.7 # TODO implement from shape given mass...?
        self.mass = 1292.2 # TODO implement, from additional argument ?
        
        self.center_gravity_rear_axle = Shape.length * 1.534 / (1.534 + 1.006) # TODO BAD assumes OrientedRectangle Shape  
        self.center_gravity_front_axle = Shape.length - self.center_gravity_rear_axle # TODO BAD assumes axle is end of vehicle
        
        self.friction_coeff = 1.0 # TODO

    def _segalLateralForce_model(self): # TODO implement
        """
        returns 
        """
        self.lateral_tire_force_front = 0.0
        self.lateral_tire_force_rear = 0.0
        pass
    
    def _threeDegFreedom_model(self, x_vec, t):
        """
        Equations of motion of the three-degree-of-freedom vehicle model. For more details see theory section.
        Retruns time derivatives of input vector:
            x1 : yaw rate
            x2 : lateral velocity
            x3 : longitudinal velocity
            x4 : longitudinal position with respect to fixed reference  
            x5 : lateral position with respece to fixed reference
            x6 : yaw angle
        """
        x1, x2, x3, x4, x5, x6 = x_vec

        a = self.center_gravity_front_axle
        b = self.center_gravity_rear_axle
        delta = self.steering_angle
        P_f = 1.0
        P_r = 1.0
        F_f = 1.0
        F_r = 1.0

        dx1dt = ( a * P_f * delta + b * F_f - b * F_r         ) / self.yaw_inertia
        dx2dt = (     P_f * delta +     F_f +     F_r         ) / self.mass - x3 * x1
        dx3dt = (     P_f         +     P_r -     F_r * delta ) / self.mass - x2 * x1
        dx4dt = - x2 * np.sin(x6) + x3 * np.cos(x6)
        dx5dt =   x2 * np.cos(x6) + x3 * np.sin(x6)
        dx6dt = x1

        return [dx1dt, dx2dt, dx3dt, dx4dt, dx5dt, dx6dt]


    def _solve_via_RK45(self):
        pass