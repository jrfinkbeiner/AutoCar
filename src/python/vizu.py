import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



class VizuManager(object): # TODO possibly already an 
    def __init__(self, World):
        super().__init__()
        self.qapp = QApplication()#sys.argv)
        # print(sys.argv)
        self.app = ApplicationWindow('World')





class ApplicationWindow(QMainWindow):

    def __init__(self, World):
        super().__init__()
        self.World = World

        self.left = 10
        self.top = 10
        self.title = 'PyQt5 matplotlib example - pythonspot.com'
        self.width = 640
        self.height = 400
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        Canvas = PlotCanvas(self, width=5, height=4)
        Canvas.move(0,0)

        button = QPushButton('PyQt5 button', self)
        button.setToolTip('This s an example button')
        button.move(500,0)
        button.resize(140,100)

        Canvas.start_timer()
        self.show()


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(figure=fig)
        self.setParent(parent)

        self._init_static_axis()
        self._init_dynamic_axis()


        print('DONE AXIS INIT')
        self.plot_canvas()
        print('DONE PLOT')

        self._timer = self.new_timer(
            100, [(self._update_canvas, (), {})])

        # print('SET TIMER')


    def start_timer(self):
        self._timer.start()
        print('STARTED TIMER')

    def _init_static_axis(self):
        self.setSizePolicy( # TODO what is this ?
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        self.updateGeometry() # TODO what is this ?
        self._static_ax = self.figure.subplots()


    def _init_dynamic_axis(self):
        self._dynamic_ax = self._static_ax.twinx().twiny()


    def _update_canvas(self):
        self._dynamic_ax.clear()
        self._plot_dynamic_ax()
        self._dynamic_ax.figure.canvas.draw()


    def plot_canvas(self):
        self._plot_static_ax()
        self._plot_dynamic_ax()
        
        # TODO difference in self.draw() and specifying draw of each axis?
        self.draw()
        # self._dynamic_ax.figure.canvas.draw() 

    def _plot_static_ax(self):
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".", color='C1')

    def _plot_dynamic_ax(self):
        t = np.linspace(0, 10, 501)
        self._dynamic_ax.plot(t, np.sin(t + time.time()))

if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    # print(sys.argv)
    app = ApplicationWindow('World') # TODO
    sys.exit(qapp.exec_())