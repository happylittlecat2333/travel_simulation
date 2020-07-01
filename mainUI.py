import sys
import sqlite3
import os

import PyQt5.sip
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from mainwindows import MainWindow
import Data

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), 'travel_query.db')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    Data.load_data(cursor)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    win = MainWindow(app)
    win.show()
    # win.showUI()

    sys.exit(app.exec_())
