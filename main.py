import os
import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore

import Data
import Strategy
import mainwindows


def create_ui():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = mainwindows.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), 'travel_query.db')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    Data.load_data(cursor)

    solution = Strategy.Solution(start_place="北京", end_place="郑州", start_time="5:00", limit_time=24)  # A*算法
    path = solution.shortestPath()
    if path is None:
        print("There is no path to destination")
    else:
        print(path)

    # create_ui()
