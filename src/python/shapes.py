class Shape(object):
    def __init__(self):
        super().__init__()

class OrientedShape(Shape):
    """
    Shpape with information about its orientation.
        orientation : tuple (float ox, float oy)  
    """
    def __init__(self, orientation):
        super().__init__()
        self.orientation = orientation / sum(orientation) 



class Circle(Shape):
    def __init__(self, radius):
        super().__init__()
        self.radius = radius

class OrientedCircle(OrientedShape, Circle):
    def __init__(self):
        super().__init__()