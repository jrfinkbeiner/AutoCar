import sys
import time
import functools
from typing import Optional, Callable

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, qApp, QAction, QAbstractButton, QTreeWidgetItem
from PyQt5.QtGui import QIcon, QMouseEvent

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



class VizuManager(object): # TODO possibly already an 
    def __init__(self, World, timestep, title):
        super().__init__()
        self.qapp = QApplication(sys.argv)
        self.app = ApplicationWindow(World=World, timestep=timestep, title=title)
        sys.exit(self.qapp.exec_())

        
    

class ApplicationWindow(QMainWindow, QWidget):

    def __init__(self, World, timestep, title):
        super().__init__()
        self.World = World

        self.left = 10
        self.top = 10
        self.title = title
        self.width = 740
        self.height = 400

        self._init_UI(timestep)

    def _init_UI(self, timestep):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.Canvas = PlotCanvas(World=self.World, timestep=timestep, parent=self, width=8, height=4)
        self.Canvas.move(0,0)

        self._init_menuBar()
        
        self._init_ExitButton()
        self._init_RunAndStopButton()

        self.show()


    def _define_menu_action(self, 
                            title: str,
                            action: Callable,
                            shortcut: str = Optional,
                            statusTip: str = Optional,
                            ) -> QAction :
        """
        Creates a menu action object, an instance of QAction.
        """
        Act = QAction(title, self) 
        if shortcut != None:
            Act.setShortcut(shortcut)
        if statusTip != None:
            Act.setStatusTip(statusTip)
        Act.triggered.connect(action) 
        return Act

    def _init_menuBar(self):
        self.menubar = self.menuBar()
        self._init_fileMenu()
        self._init_editMenu() # TODO uncomment
        
    # def _init_fileMenu(self):
    #     self.fileMenu = self.menubar.addMenu('&File')
    #     exitAct = QAction('&Exit', self) 
    #     exitAct.setShortcut('Ctrl+Q')
    #     exitAct.setStatusTip('Exit application')
    #     exitAct.triggered.connect(self.exit) # TODO delete timer first...
    #     self.fileMenu.addAction(exitAct)
    

    def _init_fileMenu(self):
        # initialsize menubar titled 'File'
        self.fileMenu = self.menubar.addMenu('&File')
        
        # define actions
        exitAct = self._define_menu_action(title='&Exit',
                                            action=self.exit,
                                            shortcut='Ctrl+Q',
                                            statusTip='Exit application',
        )
        loadAct = self._define_menu_action(title='&Load map',
                                            action=self._load_map, #functools.partial(self.World.exit, b=4),
                                            shortcut='Ctrl+L',
                                            statusTip='Load a world map',
        )
        saveAct = self._define_menu_action(title='&Save world', # TODO really only save map, or whole world?
                                            action=self.World.save_world,
                                            shortcut='Ctrl+S',
                                            statusTip='Save the current world map',
        )

        # add actions to 'File' menubar
        self.fileMenu.addAction(exitAct)
        self.fileMenu.addAction(loadAct)
        self.fileMenu.addAction(saveAct)
         
    def _init_editMenu(self):
        self.editMenu = self.menubar.addMenu('&Edit')
        modAct = self._define_menu_action(title='&Modify map',
                                    action=self.exit, # TODO
                                    shortcut='Ctrl+M',
                                    statusTip='Modify the ground map by setting drivable space.',
        )
        self.editMenu.addAction(modAct)
 

    def _init_ExitButton(self):
        self.exitButton = QPushButton('Exit', self) # TODO
        self.exitButton.setToolTip('Pressing this button exits and stops the application window.') 
        self.exitButton.move(600,0)
        self.exitButton.resize(140,100)
        
        self.exitButton.clicked.connect(self.exit)


    def _init_RunAndStopButton(self):
        self._init_RunButton()
        self._init_RunStepButton()
        self._init_StopButton()


    def _init_RunButton(self):
        self.RunBtn = RunButton('Run', self)
        self.RunBtn.setToolTip('Pressing this button starts/continues running the world.') 
        self.RunBtn.move(600,100)
        self.RunBtn.resize(140,100)
    
        self.RunBtn.clicked.connect(self.RunBtn.run)

    def _init_RunStepButton(self):
        self.RunStepBtn = RunStepButton('Run Step', self) 
        self.RunStepBtn.setToolTip('Pressing this button evolvs the world one step/iteration.') 
        self.RunStepBtn.move(600,200)
        self.RunStepBtn.resize(140,100)
    
        self.RunStepBtn.clicked.connect(self.RunStepBtn.run_step)


    def _init_StopButton(self):
        self.StopBtn = StopButton('Stop', self) 
        self.StopBtn.setToolTip('Pressing this button stops running the world.') 
        self.StopBtn.move(600,300)
        self.StopBtn.resize(140,100)

        self.StopBtn.clicked.connect(self.StopBtn.stop)

    def exit(self):
        self.Canvas.stop_timer()
        del self.Canvas._timer # TODO somehow properly delete timer before self.close()
        self.close()


    def _decide_folder(self): # TODO implement
        folder = self.World.default_folder
        return folder


    def _load_map(self):
        folder = self._decide_folder()
        self.World.load_map(folder=folder)
        self.Canvas.plot_canvas()

    def mouseMoveEvent(self, e: QMouseEvent):
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)
        print('mouseMoveEvent')

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())
        print('mousePressEvent')

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None
        print('mouseReleaseEvent')




class RunButton(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.app = parent
        self.setCheckable(True)

    def run(self):
        if self.isChecked():
            if self.app.StopBtn.isChecked():
                self.app.StopBtn.toggle()
            self.app.Canvas.start_timer()



class RunStepButton(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.app = parent
        self.setCheckable(True)

    def run_step(self):
        if not self.app.StopBtn.isChecked():
            self.app.StopBtn.stop()

        # if self.app.RunBtn.isChecked():
        #     self.app.RunBtn.toggle()
        self.app.Canvas._update()
        self.toggle()


class StopButton(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.app = parent
        self.setCheckable(True)
        self.toggle()

    def stop(self):
        if self.isChecked():
            if self.app.RunBtn.isChecked():
                self.app.RunBtn.toggle()
        self.app.Canvas.stop_timer()


class PlotCanvas(FigureCanvas):

    def __init__(self, World, timestep, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(figure=fig)
        self.setParent(parent)

        self.World = World
        self.timestep = 1000 * timestep
        self._init_axis()
        self.plot_canvas()

        self._timer = self.new_timer(
            self.timestep, [(self._update, (), {})])

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

    def _update(self): # TODO first update plot or run world step?
        self._update_canvas()
        self.World.run_step()

    def _update_canvas(self): # TODO more necessary if DynamicObject instances changed (new/old DynamicObject appears/disappears) and therefore patch instance...
        self.draw() # already enough if patches are changed by world updates!

    def plot_canvas(self):
        self._plot_static_canvas()
        self._plot_dynamic_patches()
        self.draw()

    def _plot_static_canvas(self):
        self._ax.imshow(self.World.ground_map, extent=[0, self.World.len_y, self.World.len_x, 0]) # , aspect=self.World.scale)
        for patch in self.World.static_patches.values():
            print(patch)
            self._ax.add_patch(patch)

    def _plot_dynamic_patches(self):
        for patch in self.World.dynamic_patches.values():
            print(patch)
            self._ax.add_patch(patch)

    def _replot_dynamic_patches(self): # TODO NOT USED don't add but adjust, actually neccessary as patch should already be changed..?
        for patch in self.World.dynamic_patches.values():
            print(patch)
            self._ax.add_patch(patch)



# from world import SquareWorld

if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    print(sys.argv)
    app = ApplicationWindow(World='World', title='title') # TODO
    sys.exit(qapp.exec_())