import sys
import sqlite3
import os

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from mainwindows import MainWindow
import Data

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), 'travel_query.db')    # 打开数据库
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    Data.load_data(cursor)  # 从数据库加载数据

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 适应不同分辨率
    app = QApplication(sys.argv)

    win = MainWindow(app)   # 新建窗口
    win.show()  # 显示窗口

    sys.exit(app.exec_())
