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
CANVASWIDTH = 400
CANVASHEIGHT = 500
WIDTH = 3
HEIGHT = 4
TARGETSIZE = 40
TARGETSPACE = 60
REPETITIONS = 3
pd.set_option("display.max_rows", None, "display.max_columns", None)





class Test:
    def __init__(self):
        # self.color_palette = pd.read_csv(url_color_csv)
        self.column_names = ["ID", "Condition", "Repetition", "Target(Index, relative Postition)",
                             "Targetposition(absolute)", "Targetsize(absolute)",
                             "Timestamp(Teststart)", "Timestamp(Rep_load)"]
        self.log_data = pd.DataFrame(columns=self.column_names)
        self.path_results = "result.csv"
        self.participant_ID = None
        self.participant_Condition = "normal"

    def setup_target(self):
        index = random.randrange(0, WIDTH * HEIGHT)
        pos_x = random.randrange(0, TARGETSPACE - TARGETSIZE)
        pos_y = random.randrange(0, TARGETSPACE - TARGETSIZE)
        return str(index) + ", " + str(pos_x) + ", " + str(pos_y)

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
            self.currentTest[self.column_names[4]] = time.time()
            return
        self.currentTest.loc[rep_status, self.column_names[case + 8]] = time.time()

    def set_target_abs_pos(self, rep_status, pos_x, pos_y):
        self.currentTest.loc[rep_status, self.column_names[4]] = str(pos_x) + ", " + str(pos_y)

    def get_current_target(self, rep_status):
        return self.currentTest.loc[rep_status, self.column_names[3]]



class PointingExperiment(QDialog):

    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTime()
        self.canvas_margin_top = 50
        self.initUI()
        self.canvas_margin_top = 50
        test = Test()
        test.create_test("345")
        test.save_test()

        # self.p_id = p_id
        # self.sizes = sizes
        # self.distances = distances
        # self.repetitions = repetitions
        # # gives us a list of (distance, width) tuples:
        # self.targets = repetitions * list(itertools.product(distances, sizes))
        # random.shuffle(self.targets)
        # self.elapsed = 0
        # self.mouse_moving = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
        for i in range(0, WIDTH):
            for j in range(0, HEIGHT):
                painter.drawEllipse(40 * i + 40, 50 * j + 50, 40, 40)

    def initUI(self):
        # initialize important ui-components
        uic.loadUi("Pointing_exp.ui", self)
        self.setWindowTitle('Pointing Experiment')
        self.layout = QVBoxLayout()
        # self.resize(800, 600)

    def currentTarger(self):

        return


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = PointingExperiment()

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
