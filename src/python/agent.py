import numpy as np


class Agent(object):
    """
    Agent that acts in World.
        initial_position : tuple of floates, intitail position in World in metres

    """
    def __init__(self, World=None, initial_position=None):
        super().__init__()
        self.current_position = initial_position
        self.observable_world = None
        
        if not World==None:
            self.observe_world(World, self.current_position) # really necessary in init?


    def observe_world(self, World, position):

        assert isinstance(World, SquareWorld), f"Expects instance of type SquareWorld, got {type(World)}"
        self.observable_world = World # TODO reduce to imperfect world, not whole world is known at each timestep




from .world import SquareWorld # has to be at the end of module due to circular imports
