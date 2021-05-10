import configparser
import sys
import random
import math
import itertools
from pathlib import Path

from PyQt5 import QtGui, QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QBrush, QPen, QPixmap
import pandas as pd
import random
from PyQt5.QtCore import Qt
import time

HEADERSIZE = 50
CANVAS_MIN_WIDTH = 200
CANVAS_MIN_HEIGHT = 100
TARGETS_PER_ROW = 15
TARGETS_PER_COLUMN = 7
TARGETSIZE = 40
TARGETSPACE = 60
REPETITIONS = 3
ID = 345
pd.set_option("display.max_rows", None, "display.max_columns", None)





class Test:
    def __init__(self):
        # self.color_palette = pd.read_csv(url_color_csv)
        self.column_names = ["ID", "Condition", "Repetition", "Targetindex",
                             "Targetposition(absolute)", "Targetsize(absolute)",
                             "Timestamp(Teststart)", "Timestamp(Rep_load)"]
        self.log_data = pd.DataFrame(columns=self.column_names)
        self.path_results = "result.csv"
        self.participant_ID = 345
        self.participant_Condition = "normal"

    def setup_target(self):
        index = random.randrange(0, TARGETS_PER_ROW * TARGETS_PER_COLUMN)
        return index

    def create_test(self, p_id):
        # creates test on command and fills the table
        self.participant_ID = p_id
        self.set_res_path()
        target = [None] * REPETITIONS
        self.log_data[self.column_names[2]] = target
        for i in range(0, REPETITIONS):
            target[i] = self.setup_target()
        self.log_data[self.column_names[0]] = self.participant_ID
        self.log_data[self.column_names[1]] = self.participant_Condition
        self.log_data[self.column_names[2]] = self.log_data.index
        self.log_data[self.column_names[3]] = target
        self.log_data[self.column_names[5]] = TARGETSIZE

        print(self.log_data)

    def set_res_path(self):
        self.path_results = "result_ID" + self.participant_ID + ".csv"

    def save_test(self):
        # saves table to "results.csv"
        path_results = self.path_results
        file = Path(path_results)
        if file.is_file():
            self.path_results = self.rename_filepath(path_results)
            self.save_test()
            return
        self.log_data.to_csv(path_results, index=False)

    def rename_filepath(self, fpath):
        fpath = fpath.split(".")
        return fpath[0] + "~." + fpath[1]

    # getter and setter:

    def set_timestamp(self, rep_status, case):
        if case == 0:
            self.log_data[self.column_names[4]] = time.time()
            return
        self.log_data.loc[rep_status, self.column_names[case + 8]] = time.time()

    def set_target_abs_pos(self, rep_status, pos_x, pos_y):
        self.log_data.loc[rep_status, self.column_names[4]] = str(pos_x) + ", " + str(pos_y)

    def get_current_target(self, rep_status):
        return self.log_data.loc[rep_status, self.column_names[3]]




class PointingExperiment(QDialog):

    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTime()
        self.canvas_margin_top = 70
        self.canvas_margin_default = 15
        self.test_started = False
        self.test = Test()
        self.test.create_test(str(ID))
        self.current_target_pos_x = 0
        self.current_target_pos_y = 0
        self.current_target_index = 0
        self.current_repetition = 0
        self.initUI()
        # self.p_id = p_id
        # self.sizes = sizes
        # self.distances = distances
        # self.repetitions = repetitions
        # # gives us a list of (distance, width) tuples:
        # self.targets = repetitions * list(itertools.product(distances, sizes))
        # random.shuffle(self.targets)
        # self.elapsed = 0
        # self.mouse_moving = False

    def start_test(self):
        self.test_started = True
        self.start_Button.hide()
        return

    def paintEvent(self, event):
        if self.test_started:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            index = 0
            for i in range(0, TARGETS_PER_ROW):
                for j in range(0, TARGETS_PER_COLUMN):
                    painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
                    pos_x = random.randrange(0, TARGETSPACE - TARGETSIZE) + i*TARGETSPACE + self.canvas_margin_default
                    pos_y = random.randrange(0, TARGETSPACE - TARGETSIZE) + j*TARGETSPACE + self.canvas_margin_top
                    if index == self.test.get_current_target(self.current_repetition):
                        self.current_target_pos_x = pos_x
                        self.current_target_pos_y = pos_y
                        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
                    painter.drawEllipse(pos_x, pos_y, TARGETSIZE, TARGETSIZE)
                    index = index + 1

    def initUI(self):
        # initialize important ui-components
        uic.loadUi("Pointing_exp.ui", self)
        self.setWindowTitle('Pointing Experiment')
        width = TARGETS_PER_ROW * TARGETSPACE
        height = TARGETS_PER_COLUMN * TARGETSPACE
        if width < CANVAS_MIN_WIDTH:
            width = CANVAS_MIN_WIDTH
        if height < CANVAS_MIN_HEIGHT:
            height = CANVAS_MIN_HEIGHT
        self.setFixedSize(width+2*self.canvas_margin_default, height+2*self.canvas_margin_default+self.canvas_margin_top)
        self.label.setText(str(ID))
        self.start_Button.clicked.connect(lambda: self.start_test())

    def currentTarger(self):

        return


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = PointingExperiment()

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
