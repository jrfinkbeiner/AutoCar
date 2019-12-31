import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



class VizuManager(object): # TODO possibly already an 
    def __init__(self, World, title):
        super().__init__()
        self.qapp = QApplication(sys.argv)
        print(sys.argv)
        self.app = ApplicationWindow(World=World, title=title)
        sys.exit(self.qapp.exec_())

        
    

class ApplicationWindow(QMainWindow):

    def __init__(self, World, title):
        super().__init__()
        self.World = World

        self.left = 10
        self.top = 10
        self.title = title
        self.width = 640
        self.height = 400
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        Canvas = PlotCanvas(World=self.World, parent=self, width=5, height=4)
        Canvas.move(0,0)

        button = QPushButton('PyQt5 button', self) # TODO
        button.setToolTip('This s an example button') # TODO
        button.move(500,0)
        button.resize(140,100)

        Canvas.start_timer()
        self.show()


class PlotCanvas(FigureCanvas):

    def __init__(self, World, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(figure=fig)
        self.setParent(parent)

        self.World = World

        self._init_axis()
        self.plot_canvas()

        self._timer = self.new_timer(
            100, [(self._update_canvas, (), {})])

        # print('SET TIMER')


    def start_timer(self):
        self._timer.start()
        print('STARTED TIMER')

    def _init_axis(self):
        self.setSizePolicy( # TODO what is this ?
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        self.updateGeometry() # TODO what is this ?
        self._ax = self.figure.subplots(1)
        self._ax.grid()


    def _update_canvas(self):
        # self._replot_dynamic_patches()
        # TODO to be del just chekcing
        print(time.time())
        self.World.dynamicObjs[0].Shape.orientation = np.dot(np.array(self.World.dynamicObjs[0].Shape.orientation), np.array([[np.cos(time.time()), np.sin(time.time())], [-np.sin(time.time()), np.cos(time.time())]]))
        print(self.World.dynamicObjs[0].Shape.orientation)
        
        self.World.dynamicObjs[0].Shape.update_patch(self.World.dynamic_patches[0], self.World.dynamicObjs[0].position)
        print(self.World.dynamicObjs[0].Shape)
        self.draw() # already enough?!


    def plot_canvas(self):
        self._plot_static_canvas()
        self._plot_dynamic_patches()
        # TODO difference in self.draw() and specifying draw of each axis?
        self.draw()
        print('drawn')

    def _plot_static_canvas(self):
        self._ax.imshow(self.World.ground_map)
        for patch in self.World.static_patches.values():
            print(patch)
            self._ax.add_patch(patch)


    def _plot_dynamic_patches(self):
        for patch in self.World.dynamic_patches.values():
            print('HEY')
            print(patch)
            self._ax.add_patch(patch)

    def _replot_dynamic_patches(self): # TODO don't add but adjust, actually neccessary as patch should already be changed..?
        for patch in self.World.dynamic_patches.values():
            print(patch)
            self._ax.add_patch(patch)



# from world import SquareWorld

if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    print(sys.argv)
    app = ApplicationWindow(World='World', title='title') # TODO
    sys.exit(qapp.exec_())