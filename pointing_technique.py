
import configparser
import sys
import random
import math
import itertools
from pathlib import Path
import os
import mouse

import PyQt5.QtGui
from PyQt5 import QtGui, QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen, QPixmap, QCursor
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
condition_selection = ["normal"]
pd.set_option("display.max_rows", None, "display.max_columns", None)



class Test:
    def __init__(self):
        # self.color_palette = pd.read_csv(url_color_csv)
        self.column_names = ["ID", "Condition", "Repetition", "Target Index",
                             "Target Position(relative)", "Target Size(absolute)",
                             "Timestamp(Teststart)", "Timestamp(Rep_load)", "Timestamp(clicked)",
                             "Pointer Postition(start, absolute)", "Pointer Postition(end, absolute)", "Pointer Postition(end, relative)"]
        self.log_data = pd.DataFrame(columns=self.column_names)
        self.path_results = "result.csv"
        self.participant_ID = 0
        self.pos_conditons = condition_selection
        self.participant_Condition = ["normal"] * repetitions

    @staticmethod
    def setup_target():
        index = random.randrange(0, targets_per_row * targets_per_column)
        return index

    def create_test(self, p_id):
        # creates test on command and fills the table
        self.participant_ID = p_id
        self.set_res_path()
        index = 0
        while index < repetitions:
            for j in range(0, len(self.pos_conditons)):
                self.participant_Condition[index + j] = str(self.pos_conditons[j])
                if index == repetitions - 1:
                    break
            index = index + j + 1
            self.condition_roulette()
        target = [None] * repetitions
        self.log_data[self.column_names[2]] = target
        for i in range(0, repetitions):
            target[i] = self.setup_target()
        self.log_data[self.column_names[0]] = self.participant_ID
        print(self.participant_Condition)
        self.log_data[self.column_names[1]] = self.participant_Condition
        self.log_data[self.column_names[2]] = self.log_data.index
        self.log_data[self.column_names[3]] = target
        self.log_data[self.column_names[5]] = targetsize


    def condition_roulette(self):
        temp_cond = self.pos_conditons[0]
        for i in range(0, len(self.pos_conditons)):
            if i == (len(self.pos_conditons) - 1):
                self.pos_conditons[i] = temp_cond
                break
            self.pos_conditons[i] = self.pos_conditons[i + 1]

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

    def set_target_rel_pos(self, rep_status, position):
        self.log_data.loc[rep_status, self.column_names[4]] = position

    def set_po_pos(self, rep_status, case, position):
        self.log_data.loc[rep_status, self.column_names[9 + case]] = position

    def get_current_target(self, rep_status):
        return self.log_data.loc[rep_status, self.column_names[3]]

    def get_current_con(self, rep_status):
        return self.log_data.loc[rep_status, self.column_names[1]]


class PointingExperiment(QDialog, QtWidgets.QGraphicsView):

    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTime()
        self.canvas_margin_top = 70
        self.canvas_margin_default = 15
        self.test_started = False
        self.canvas_updated = False
        self.current_target_pos_x = 0
        self.current_target_pos_y = 0
        self.current_target_index = 0
        self.current_repetition = 0
        self.test = Test()
        self.test.create_test(str(id))
        self.initUI()
        self.setMouseTracking(True)

    #https://stackoverflow.com/questions/25368295/qwidgetmousemoveevent-not-firing-when-cursor-over-child-widget
    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)

        QWidget.setMouseTracking(self, flag)
        recursive_set(self)

    def start_test(self):
        self.test_started = True
        self.test.set_timestamp(self.current_repetition, 0)
        self.start_Button.hide()
        return

    def paintEvent(self, event):
        self.label.setText("ID: " + str(id) + " - " + str(self.current_repetition + 1) + "/" + str(repetitions))
        if self.test_started & (not self.canvas_updated):
            condition = str(self.test.get_current_con(self.current_repetition))
            painter_color = Qt.black
            painter_color_fill = Qt.gray
            if condition == "Color: green":
                painter_color = Qt.green
                painter_color_fill = Qt.darkGreen
            if condition == "Color: red":
                painter_color = Qt.red
                painter_color_fill = Qt.darkRed
            painter = QPainter(self)
            painter.setPen(QPen(painter_color, 2, Qt.SolidLine))
            index = 0
            for i in range(0, targets_per_row):
                for j in range(0, targets_per_column):
                    painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
                    pos_x = random.randrange(0, targetspace - targetsize) + i * targetspace + self.canvas_margin_default
                    pos_y = random.randrange(0, targetspace - targetsize) + j * targetspace + self.canvas_margin_top
                    if index == self.test.get_current_target(self.current_repetition):
                        self.current_target_pos_x = pos_x
                        self.current_target_pos_y = pos_y
                        painter.setBrush(QBrush(painter_color_fill, Qt.SolidPattern))
                        self.test.set_target_rel_pos(self.current_repetition, pyautogui.Point(pos_x, pos_y))
                    painter.drawEllipse(pos_x, pos_y, targetsize, targetsize)
                    index = index + 1
            self.test.set_timestamp(self.current_repetition, 1)
            self.test.set_po_pos(self.current_repetition, 0, pyautogui.position())
            self.canvas_updated = True

    def check_input(self, m_pos_x, m_pos_y):
        if self.current_target_pos_x > m_pos_x:
            return
        if self.current_target_pos_y > m_pos_y:
            return
        if (self.current_target_pos_y + targetsize) < m_pos_y:
            return
        if (self.current_target_pos_x + targetsize) < m_pos_x:
            return
        print("success!!")
        self.test.set_timestamp(self.current_repetition, 2)
        self.test.set_po_pos(self.current_repetition, 1, pyautogui.position())
        self.test.set_po_pos(self.current_repetition, 2, pyautogui.Point(m_pos_x, m_pos_y))
        print(self.test.log_data)
        self.update()

    def update(self):
        super().update()
        if self.test_started:
            if self.current_repetition + 1 < repetitions:
                self.current_repetition = self.current_repetition + 1
                self.canvas_updated = False
                return
            self.test_started = False
            self.test.save_test()
            self.close()

    def mouseMoveEvent(self, event):
        if self.test_started:
            if event.type() == QtCore.QEvent.MouseMove:
                print("mouse moved!")
                self.check_cursor_for_near_target(event.x(), event.y())

    def check_cursor_for_near_target(self, m_pos_x, m_pos_y):
            cursor_distance_to_target_x = self.current_target_pos_x - m_pos_x + targetsize/2
            cursor_distance_to_target_y = self.current_target_pos_y - m_pos_y + targetsize/2

            print("the cursors distance to target: ",cursor_distance_to_target_x, cursor_distance_to_target_y)

            if abs(cursor_distance_to_target_x) < targetsize and abs(cursor_distance_to_target_y) < targetsize:
                if(cursor_distance_to_target_x > 0 and cursor_distance_to_target_y > 0):
                    mouse.move(cursor_distance_to_target_x, cursor_distance_to_target_y, absolute=False, duration=0.2)
                if(cursor_distance_to_target_x > 0 and cursor_distance_to_target_y < 0):
                    mouse.move(cursor_distance_to_target_x, -cursor_distance_to_target_y,absolute=False, duration=0.2)
                if(cursor_distance_to_target_x < 0 and cursor_distance_to_target_y < 0):
                    mouse.move(-cursor_distance_to_target_x, -cursor_distance_to_target_y, absolute=False, duration=0.2)
                if(cursor_distance_to_target_x < 0 and cursor_distance_to_target_y > 0):
                    mouse.move(-cursor_distance_to_target_x, cursor_distance_to_target_y, absolute=False, duration=0.2)

          #  mouse.move(self.current_target_pos_x, self.current_target_pos_y)
           # print("mouse moved to target position!")

    def mousePressEvent(self, event):
        if self.test_started:
            if event.button() == QtCore.Qt.LeftButton:
                self.check_input(event.x(), event.y())
                print("mouse pressed!")
                #mouse.move(500,500)


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



def init_args_handler():  # how to handle the possible arguments (Dialogtree u.a)
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


def exception_handler(case):  # exiting earlier due to .. reasons
    print(dialog(case))
    sys.exit()


def dialog(case):
    switch = {  # a simple dialog manager
        "NoArgs": "Please provide a configuration file & an ID as arguments!",
        "noFile": "Couldn't open file!",
        "noID": "Please provide participant ID!",
        "noInput": "Missing input from configuration file!\n\n"
                   "Please Provide following settings in category \'Canvas_Settings\':\n"
                   "\'CanvasMinWidth\', \'CanvasMinHeight\'\n\n"
                   "...and the following settings in category \'Test_Settings\':\n"
                   "\'TargetsPerRow\', \'TargetsPerColumn\', \'TargetSize\', \'TargetSpace\', \'Repetitions\', \'Conditions\'\n"
    }
    return switch.get(case)


def get_presets():
    global canvas_min_width, canvas_min_height, targets_per_row, targets_per_column, targetsize, targetspace, repetitions, condition_selection
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
        condition_selection = config['Test_Settings']['Conditions'].split(", ")
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