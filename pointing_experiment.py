import configparser
import sys
import random
import math
import itertools
from pathlib import Path
import os
from PyQt5 import QtGui, QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QBrush, QPen, QPixmap
import pandas as pd
import random
from PyQt5.QtCore import Qt
import time
import pyautogui

config_url = 'setup.ini'
canvas_min_width = 200
canvas_min_height = 100
targets_per_row = 15
targets_per_column = 7
targetsize = 40
targetspace = 60
repetitions = 3
id = 345
pd.set_option("display.max_rows", None, "display.max_columns", None)

class Test:
    def __init__(self):
        # self.color_palette = pd.read_csv(url_color_csv)
        self.column_names = ["ID", "Condition", "Repetition", "Target Index",
                             "Target Position(relative)", "Target Size(absolute)",
                             "Timestamp(Teststart)", "Timestamp(Rep_load)", "Timestamp(clicked)", "Pointer Postition(start)", "Pointer Postition(end)"]
        self.log_data = pd.DataFrame(columns=self.column_names)
        self.path_results = "result.csv"
        self.participant_ID = 0
        self.participant_Condition = "normal"

    @staticmethod
    def setup_target():
        index = random.randrange(0, targets_per_row * targets_per_column)
        return index

    def create_test(self, p_id):
        # creates test on command and fills the table
        self.participant_ID = p_id
        self.set_res_path()
        target = [None] * repetitions
        self.log_data[self.column_names[2]] = target
        for i in range(0, repetitions):
            target[i] = self.setup_target()
        self.log_data[self.column_names[0]] = self.participant_ID
        self.log_data[self.column_names[1]] = self.participant_Condition
        self.log_data[self.column_names[2]] = self.log_data.index
        self.log_data[self.column_names[3]] = target
        self.log_data[self.column_names[5]] = targetsize

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

    @staticmethod
    def rename_filepath(fpath):
        fpath = fpath.split(".")
        return fpath[0] + "~." + fpath[1]

    # getter and setter:

    def set_timestamp(self, rep_status, case):
        if case == 0:
            self.log_data[self.column_names[6 + case]] = time.time()
            return
        self.log_data.loc[rep_status, self.column_names[6 + case]] = time.time()

    def set_target_abs_pos(self, rep_status, pos_x, pos_y):
        self.log_data.loc[rep_status, self.column_names[4]] = "(" + str(pos_x) + ", " + str(pos_y) + ")"

    def set_po_pos(self, rep_status, case, position):
        self.log_data.loc[rep_status, self.column_names[9 + case]] = position

    def get_current_target(self, rep_status):
        return self.log_data.loc[rep_status, self.column_names[3]]


class PointingExperiment(QDialog):

    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTime()
        self.canvas_margin_top = 70
        self.canvas_margin_default = 15
        self.test_started = False
        self.current_target_pos_x = 0
        self.current_target_pos_y = 0
        self.current_target_index = 0
        self.current_repetition = 0
        self.test = Test()
        self.test.create_test(str(id))
        self.initUI()

    def start_test(self):
        self.test_started = True
        self.test.set_timestamp(self.current_repetition, 0)
        self.start_Button.hide()
        return

    def paintEvent(self, event):
        self.label.setText("ID: " + str(id) + " - " + str(self.current_repetition + 1) + "/" + str(repetitions))
        if self.test_started:

            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            index = 0
            for i in range(0, targets_per_row):
                for j in range(0, targets_per_column):
                    painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
                    pos_x = random.randrange(0, targetspace - targetsize) + i * targetspace + self.canvas_margin_default
                    pos_y = random.randrange(0, targetspace - targetsize) + j * targetspace + self.canvas_margin_top
                    if index == self.test.get_current_target(self.current_repetition):
                        self.current_target_pos_x = pos_x
                        self.current_target_pos_y = pos_y
                        painter.setBrush(QBrush(Qt.darkGreen, Qt.SolidPattern))
                        self.test.set_target_abs_pos(self.current_repetition, pos_x, pos_y)
                    painter.drawEllipse(pos_x, pos_y, targetsize, targetsize)
                    index = index + 1
            self.test.set_timestamp(self.current_repetition, 1)
            self.test.set_po_pos(self.current_repetition, 0, pyautogui.position())


    def check_input(self, m_pos_x, m_pos_y):
        if self.current_target_pos_x > m_pos_x:
            return
        if self.current_target_pos_y > m_pos_y:
            return
        if self.current_target_pos_y + targetsize < m_pos_y:
            return
        if self.current_target_pos_x + targetsize < m_pos_x:
            return
        print("success!!")
        self.test.set_timestamp(self.current_repetition, 2)
        self.test.set_po_pos(self.current_repetition, 1, pyautogui.position())
        print(self.test.log_data)
        self.update()

    def update(self):
        super().update()
        if self.test_started:
            if self.current_repetition + 1 < repetitions:
                self.current_repetition = self.current_repetition + 1
                return
            self.test_started = False
            self.test.save_test()
            self.close()

    def mousePressEvent(self, event):
        if self.test_started:
            if event.button() == QtCore.Qt.LeftButton:
                self.check_input(event.x(), event.y())

    def initUI(self):
        # initialize important ui-components
        uic.loadUi("Pointing_exp.ui", self)
        self.setWindowTitle('Pointing Experiment')
        width = targets_per_row * targetspace
        height = targets_per_column * targetspace
        if width < canvas_min_width:
            width = canvas_min_width
        if height < canvas_min_height:
            height = canvas_min_height
        self.setFixedSize(width + 2 * self.canvas_margin_default,
                          height + 2 * self.canvas_margin_default + self.canvas_margin_top)
        self.label.setText("ID: " + str(id) + " - 0/" + str(repetitions))
        self.start_Button.clicked.connect(lambda: self.start_test())



def init_args_handler():    # how to handle the possible arguments (Dialogtree u.a)
    global id
    global config_url
    if len(sys.argv) != 3:
        exception_handler("NoArgs")
    if not (os.path.isfile(sys.argv[1])):
        exception_handler("noFile")
    if not isinstance(int(sys.argv[2]), int):
        exception_handler("noID")
    config_url = sys.argv[1]
    id = sys.argv[2]
    return

def exception_handler(case):    # exiting earlier due to .. reasons
    print(dialog(case))
    sys.exit()

def dialog(case):
    switch = {                  # a simple dialog manager
        "NoArgs": "Please provide a configuration file & an ID as arguments!",
        "noFile": "Couldn't open file!",
        "noID": "Please provide participant ID!",
        "noInput": "Missing input from configuration file!\n\n"
                   "Please Provide following settings in category \'Canvas_Settings\':\n"
                   "\'CanvasMinWidth\', \'CanvasMinHeight\'\n\n"
                   "...and the following settings in category \'Test_Settings\':\n"
                   "\'TargetsPerRow\', \'TargetsPerColumn\', \'TargetSize\', \'TargetSpace\', \'Repetitions\'\n"
    }
    return switch.get(case)

def get_presets():
    global canvas_min_width, canvas_min_height, targets_per_row, targets_per_column, targetsize, targetspace, repetitions
    init_args_handler()
    config = configparser.ConfigParser()
    config.read(config_url)
    try:
        canvas_min_width = int(config['Canvas_Settings']['CanvasMinWidth'])
        canvas_min_height = int(config['Canvas_Settings']['CanvasMinHeight'])
        targets_per_row = int(config['Test_Settings']['TargetsPerRow'])
        targets_per_column = int(config['Test_Settings']['TargetsPerColumn'])
        targetsize = int(config['Test_Settings']['TargetSize'])
        targetspace = int(config['Test_Settings']['TargetSpace'])
        repetitions = int(config['Test_Settings']['Repetitions'])
    except KeyError:
        exception_handler("noInput")



def main():
    get_presets()
    app = QtWidgets.QApplication(sys.argv)
    win = PointingExperiment()

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
