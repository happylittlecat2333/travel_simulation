from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QObject
from PyQt5 import uic
from PyQt5.QtGui import QPainter, QFont, QPixmap, QColor
from PyQt5.QtCore import Qt, QTime

import os
import threading
import time

import Data
import Strategy


def sum_time(str_time):
    time_list = list(map(int, str_time.split(":")))
    return time_list[0] * 60 + time_list[1]


class MainWindow(QMainWindow):
    def __init__(self, qApp=None):
        super(MainWindow, self).__init__()
        ui_file = os.path.join(os.path.dirname(__file__), 'mainwindow.ui')
        self.gui = uic.loadUi(ui_file, self)

        self.solution = Strategy.Solution()
        self.map_pic = QPixmap("./map_test.jpg")
        self.current_x = 0
        self.current_y = 0
        self.start_time = ""
        self.path = []
        self.set_traveller = False

        self.set_initial()
        self.pushButton_compute.clicked.connect(self.compute_clicked)
        self.pushButton_simulate.clicked.connect(self.simulate_clicked)
        self.comboBox_kind.currentIndexChanged.connect(self.kind_changed)

    def set_initial(self):
        for i in range(len(Data.all_place)):
            self.comboBox_start.addItem(Data.all_place[i])
            self.comboBox_end.addItem(Data.all_place[i])
        self.comboBox_start.setCurrentIndex(0)
        self.comboBox_end.setCurrentIndex(0)

        self.comboBox_kind.addItem("最小风险策略")
        self.comboBox_kind.addItem("限时最小风险策略")
        self.comboBox_kind.setCurrentIndex(0)
        self.timeEdit.setTime(QTime.fromString("07:00", 'hh:mm'))
        self.timeEdit.setDisplayFormat("HH:mm")
        self.label_log.setText("请按下计算策略，得到可用路线")
        self.comboBox_limit_time.setEnabled(False)

        for i in range(10):
            self.comboBox_limit_time.addItem(str((i + 1) * 6)+" h")
        self.comboBox_limit_time.setCurrentIndex(3)  # 默认24小时

    def kind_changed(self):
        if self.comboBox_kind.currentIndex() is 0:
            self.comboBox_limit_time.setEnabled(False)
        else:
            self.comboBox_limit_time.setEnabled(True)

    def compute_clicked(self):
        start_place = Data.all_place[self.comboBox_start.currentIndex()]
        end_place = Data.all_place[self.comboBox_end.currentIndex()]
        self.start_time = self.timeEdit.time().toString("hh:mm")
        print(self.start_time)
        limit_time = -1  # 默认最小风险策略
        if self.comboBox_kind.currentIndex() is 1:  # 限时风险策略
            limit_time = (self.comboBox_limit_time.currentIndex() + 1) * 6
        print(limit_time)
        self.path = self.solution.shortestPath(start_place=start_place, end_place=end_place,
                                               start_time=self.start_time, limit_time=limit_time)

        if self.path is None:
            self.label_log.setText("不存在可用路线")
            if start_place == end_place:
                self.label_log.setText("目的地为出发地，已到达")
        else:
            s = ["班次表(出发地-到达地-交通工具-班次号-起始时间-路程时间)："]
            for line in self.path:
                s.append("\n  "+"-".join(line[:-1]))
            self.label_log.setText("\n".join(s))

    def simulate_clicked(self):
        t = threading.Thread(target=self.simulation, args=())
        t.start()
        # QWidget.repaint(self)
        # self.simulation()

    def simulation(self):
        if self.path is None:
            return
        self.current_x, self.current_y = Data.map_geo[self.path[0][0]]
        current_time = sum_time(self.start_time)
        # print(Data.map_geo[self.path[0][0]])
        self.set_traveller = True
        day = 0  # 旅行的第几天
        min_per_day = 24 * 60
        for line in self.path:  # 在算出的路线中，模拟旅客在不同航班的行程轨迹
            print(line)
            start_place, end_place = line[0], line[1]
            start_x, start_y = Data.map_geo[line[0]]
            end_x, end_y = Data.map_geo[line[1]]
            line_start_time = sum_time(line[4]) + day * min_per_day
            line_route_time = sum_time(line[5])
            all_day = (line_start_time + line_route_time) // min_per_day
            if (all_day - day) != 0:  # 航班的时间跨越一天
                day += 1
            inc_x = (end_x - start_x) / line_route_time
            inc_y = (end_y - start_y) / line_route_time
            inc_t = 30  # 6 （1s对映6min）
            line_already_time = 0

            while True:  # 没有到达航班的起始时间，在城市中等待航班的到来
                self.label_travel.setText("等待中：正在等待从"+start_place+"前往"+end_place+"的航班")
                time.sleep(1)
                current_time += inc_t
                QWidget.repaint(self)
                if current_time >= line_start_time:
                    current_time = line_start_time
                    break

            while True:  # 模拟旅客在航班中的行程
                self.label_travel.setText("行程信息：正在从"+start_place+"前往"+end_place+"的航班....")
                time.sleep(1)
                line_already_time += inc_t
                if line_already_time >= line_route_time:
                    self.current_x, self.current_y = end_x, end_y
                    QWidget.repaint(self)
                    break
                self.current_x += inc_x * inc_t
                self.current_y += inc_y * inc_t
                # print("current_pos:", self.current_x, self.current_y)
                QWidget.repaint(self)
            current_time = line_start_time + line_route_time

        print("finish travel")
        self.label_travel.setText("到达目的地")
        self.set_traveller = False
        time.sleep(2)
        QWidget.repaint(self)
        self.label_travel.setText("旅客行程信息")


    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(qp)
        qp.end()

    def drawText(self, qp):     # 画图，每次旅客位置更新，或初始化时重新画图
        qp.setPen(Qt.red)
        qp.setFont(QFont('Decorative', 10))
        pic_x = self.label_pic.x()  # 图片的坐标
        pic_y = self.label_pic.y()
        pic_size_x = self.label_pic.width()     # 图片的大小
        pic_size_y = self.label_pic.height()

        lon = []
        lat = []
        for key, i in Data.map_geo.items():
            lon.append(i[0])
            lat.append(i[1])
        edge = 8  # 给地图留边
        lon_min, lon_max = min(lon), max(lon)   # 经纬度的范围
        lat_min, lat_max = min(lat), max(lat)

        lon_center, lat_center = (lon_min + lon_max) / 2, (lat_min + lat_max) / 2
        pic_center_x, pic_center_y = pic_x + pic_size_x / 2, pic_y + pic_size_y / 2

        x_scale = pic_size_x / (lon_max - lon_min) - edge  # 经纬度与显示图片之间的比例
        y_scale = pic_size_y / (lat_max - lat_min) - edge

        qp.drawPixmap(pic_x, pic_y, pic_size_x, pic_size_y, self.map_pic)  # 全国地图作为背景
        qp.setBrush(QColor(25, 0, 90, 200))
        for key, value in Data.map_geo.items():  # 显示所有城市的位置
            x_pos = pic_center_x + (value[0] - lon_center) * x_scale  # 从中心按比例缩放得到的显示图片的位置
            y_pos = pic_center_y - (value[1] - lat_center) * y_scale
            qp.drawText(x_pos, y_pos, key)
            qp.drawRect(x_pos-10, y_pos-5, 5, 5)

        qp.setPen(Qt.blue)
        if self.set_traveller is True:  # 显示旅客位置
            x_pos = pic_center_x + (self.current_x - lon_center) * x_scale
            y_pos = pic_center_y - (self.current_y - lat_center) * y_scale
            qp.drawText(x_pos, y_pos - 10, "旅客")
