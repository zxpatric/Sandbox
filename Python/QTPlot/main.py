import sys
from PyQt5 import QtWidgets, QtGui
import numpy as np

import mplWidget
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class Qt4MplCanvas(mplWidget.MplCanvas):
    def __init__(self):
    # Standard Matplotlib code to generate the plot
        super().__init__()
        self.axes = self.fig.add_subplot(111)
        self.x = np.arange(0.0, 3.0, 0.01)
        self.y = np.cos(2*np.pi*self.x)
        self.axes.plot(self.x, self.y)
        # initialize the canvas where the Figure renders into

if __name__ == '__main__':
    # Create the GUI application
    qApp = QtWidgets.QApplication(sys.argv)
    # Create the Matplotlib widget
    # mpl = mplWidget.MplCanvas()
    main_widget = QtWidgets.QWidget()
    vbl = QtWidgets.QVBoxLayout(main_widget)

    mpl = Qt4MplCanvas()
    ntb = NavigationToolbar(mpl, main_widget)

    vbl.addWidget(mpl)
    vbl.addWidget(ntb)

    # show the widget
    # mpl.show()
    main_widget.show()

    # start the Qt main loop execution, exiting from this script
    # with the same return code of Qt application
    sys.exit(qApp.exec_())