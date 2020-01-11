import numpy as np
import matplotlib.patches as pat
import sys # TODO to be del

def rot_mat_from_angle(angle):
    rot_mat = np.array([
                [ np.cos(angle), np.sin(angle)],
                [-np.sin(angle), np.cos(angle)]
    ])
    return rot_mat


def inv_rot_mat_from_angle(angle):
    inv_rot_mat = rot_mat_from_angle(-angle)
    return inv_rot_mat



class Shape(object):
    def __init__(self):
        super().__init__()
    
    def matplotlib_patch(self, xy, **kwargs):
        """
        Returns a mapltplotlib.patches patch according to subclass type.
            xy = tuple, (float x, float y), center position of patch
        """
        raise NotImplementedError

    def update_patch(self, patch):
        """
        Updates a mapltplotlib.patches patch according to subclass type.
            patch = mapltplotlib.patches.patch, instance of patch calss whoch values are to be updated
        """
        raise NotImplementedError


class OrientedShape(Shape):
    """
    Shpape with information about its orientation.
        orientation : tuple (float ox, float oy)  
    """
    def __init__(self, orientation):
        super().__init__()
        self.orientation = np.asarray(orientation) / np.linalg.norm(orientation)

    def calc_rot_angle(self):
        """
        Calculates rotation angle form orientation tuple.
        """
        rot_angle = -np.arcsin(self.orientation[0])
        
        if self.orientation[1] < 0:
            if rot_angle < 0: # TODO possibly find nicer/simpler equations?
                rot_angle = -(np.pi - np.abs(rot_angle))
            else:
                rot_angle = np.pi - rot_angle
        return rot_angle


    @staticmethod
    def calc_orientation_from_angle(angle):
        """
        Calculates orientation tuple form rotation angle (right rotation, non-math way definiton of angle).
        """
        orientation = np.array([-np.sin(angle), np.cos(angle)])
        return orientation

    def orthogonal_orientation(self):
        """
        Return orhognal unit-vector to orientation vector.
        """
        return np.array([self.orientation[1], -self.orientation[0]])
                

class Circle(Shape):
    def __init__(self, radius):
        super().__init__()
        self.radius = radius

    def matplotlib_patch(self, xy, **kwargs):
        return pat.Circle(xy=xy, radius=self.radius, **kwargs)

class OrientedCircle(OrientedShape, Circle):
    def __init__(self, orientation, raidus):
        super().__init__(orientation, raidus)



class OrientedRectangle(OrientedShape):
    def __init__(self, orientation, width, length):
        super().__init__(orientation)
        self.width = width
        self.length = length

    def _calc_patch_xy_and_angle(self, xy):
        rot_angle = self.calc_rot_angle()
        rot_angle_deg = rot_angle * 180 / np.pi
        inv_rot_mat = inv_rot_mat_from_angle(rot_angle)

        rel_xy_min = np.dot([-0.5*self.width, -0.5*self.length], inv_rot_mat.T)
        xy_min = np.asarray(xy) + rel_xy_min
        return xy_min, rot_angle_deg

    def matplotlib_patch(self, xy, **kwargs):
        xy_min, rot_angle_deg = self._calc_patch_xy_and_angle(xy)
        patch = pat.Rectangle(xy=xy_min, width=self.width, height=self.length, angle=rot_angle_deg, **kwargs)
        return patch

    def update_patch(self, patch, xy): 
        # TODO give patch as property
        # TODO update orientation
        assert type(patch) == pat.Rectangle, f"Expects instance of class matplotlib.patches.Rectangle, got {type(patch)}"
        xy_min, rot_angle_deg = self._calc_patch_xy_and_angle(xy)
        patch.set_xy(xy_min)
        patch.angle = rot_angle_deg # TODO check
