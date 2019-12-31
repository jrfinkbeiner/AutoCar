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

        self.Canvas = PlotCanvas(World=self.World, parent=self, width=5, height=4)
        self.Canvas.move(0,0)


        print('\nBUTTON STUFF')
        self.init_ExitButton()
        self.init_RunAndStopButton()

        self.show()


    def init_ExitButton(self):
        self.exitButton = QPushButton('Exit', self) # TODO
        self.exitButton.setToolTip('Pressing this button exits and stops the application window') # TODO
        self.exitButton.move(500,0)
        self.exitButton.resize(140,100)
        
        self.exitButton.clicked.connect(self.exit)


    def init_RunAndStopButton(self):
        self.init_RunButton()
        self.init_StopButton()


    def init_RunButton(self):
        self.RunBtn = RunButton('Run', self) # TODO
        self.RunBtn.setToolTip('Pressing this button continues running the world.') # TODO
        self.RunBtn.move(500,150)
        self.RunBtn.resize(140,100)
    
        self.RunBtn.clicked.connect(self.RunBtn.run)


    def init_StopButton(self):
        self.StopBtn = StopButton('Stop', self) # TODO
        self.StopBtn.setToolTip('Pressing this button stops running the world.') # TODO
        self.StopBtn.move(500,300)
        self.StopBtn.resize(140,100)

        self.StopBtn.clicked.connect(self.StopBtn.stop)

    def exit(self):
        self.Canvas.stop_timer()
        del self.Canvas._timer # TODO somehow properly delete timer before self.close()
        self.close()



class RunButton(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.app = parent
        self.setCheckable(True)

    def run(self):
        if self.isChecked():
            print('run')
            self.app.StopBtn.toggle()
            self.app.Canvas.start_timer()


class StopButton(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.app = parent
        self.setCheckable(True)
        self.toggle()

    def stop(self):
        if self.isChecked():
            print('stop')
            self.app.RunBtn.toggle()
            self.app.Canvas.stop_timer()

class PlotCanvas(FigureCanvas):

    def __init__(self, World, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(figure=fig)
        self.setParent(parent)

        self.World = World

        self._init_axis()
        self.plot_canvas()

        self._timer = self.new_timer(
            500, [(self._update, (), {})])


    def start_timer(self):
        self._timer.start()


    def stop_timer(self):
        self._timer.stop()
        

    def _init_axis(self):
        self.setSizePolicy( # TODO what is this ?
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        self.updateGeometry() # TODO what is this ?
        self._ax = self.figure.subplots(1)
        self._ax.grid()


    def _update(self):
        print('')
        print(self.World.dynamic_patches[0])
        self.World.run_step()
        self._update_canvas

    def _update_canvas(self):
        self.draw() # already enough if patches are changed by world updates!


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