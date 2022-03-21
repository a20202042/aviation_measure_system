import PyQt5, PyQt5.QtWidgets, PyQt5.QtCore, qt5, PyQt5.sip
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView, QTableWidgetItem
from qt5 import Ui_MainWindow, Ui_Form, Ui_toolcheck, Ui_widget_projectcheck, Ui_check, data_check, measure_show_project, Ui_Form_system_set, tool_create, appearance_affect
import sys, re, time, serial.tools.list_ports, toolconnect, sql_connect, measure
from PyQt5.QtCore import QThread, pyqtSignal
import os, shutil, matplotlib, matplotlib.pyplot as plt, global_var as gvar, read_data_json as read_json
selected_com_port = ''
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, project_name, measure_item_data, work_order_data, measurer):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.sql = sql_connect.sql_connect()
        self.measure_value_data = []
        self.measure_yield = []
        self.drawing_data = []
        self.number = 0
        self.number_row = 0
        self.number_colum = 0
        self.row = int()
        self.column = int()
        self.column_bool = False
        self.change = False
        gvar.measure_type = ""
        self.measure_value = measure_thread()
        self.measure_value.measure_value.connect(self.setmeasurevalue)
        self.measure_value.measure_unit.connect(self.unit_check)
        self.com_name = gvar.system_com_name
        self.project_name = project_name
        self.measurer = measurer
        self.measure_item_data = []
        self.work_order_data = work_order_data
        print('專案名稱:%s' % self.project_name)
        print('工單設定:%s' % self.work_order_data)
        print('量測項目%s' % self.measure_item_data)
        self.measure_project_time = time.strftime('%Y-%m-%d', time.localtime())
        self.measure_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime())
        self.part_number = self.sql.sql_find_work_order_part_number(gvar.work_order)
        self.measure_tool_start()
        self.tb = self.addToolBar('open')
        self.new = QtWidgets.QAction(QtGui.QIcon(BASE_DIR + '\\po.png'), 'UP project', self)
        self.tb.addAction(self.new)
        self.new = QtWidgets.QAction(QtGui.QIcon(BASE_DIR + '\\project_item.png'), 'project_item', self)
        self.tb.addAction(self.new)
        self.new = QtWidgets.QAction(QtGui.QIcon(BASE_DIR + '\\measure_choose.png'), 'project_choose', self)
        self.tb.addAction(self.new)
        self.new = QtWidgets.QAction(QtGui.QIcon(BASE_DIR + '\\part_affect.png'), 'part_affect', self)
        self.tb.addAction(self.new)
        self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\GO.png'))
        self.ui.label_gonogo.setScaledContents(True)
        self.ui.label_project_name.setText('專案名稱：%s' % project_name)
        self.ui.label_project_item_name_2.setText('量測人員：%s' % self.measurer)
        self.project_item = [
         '量測部位', '量測日期', '量測次數', '良數', '不良數', '總數', 'GO/NOGO']
        self.ui.tableWidget_project_item.setRowCount(len(self.project_item))
        self.ui.tableWidget_project_item.setColumnCount(1)
        self.ui.tableWidget_project_item.horizontalHeader().setVisible(False)
        self.ui.tableWidget_project_item.setVerticalHeaderLabels(self.project_item)
        self.ui.tableWidget_project_item.setItem(0, 0, QTableWidgetItem('未選擇量測部位'))
        self.ui.tableWidget_project_item.setItem(0, 1, QTableWidgetItem(self.measure_time))
        self.ui.tableWidget_project_item.resizeColumnsToContents()
        self.measure_item = [
         '量測項目名稱', '量測數值上限', '量測數值下限', '量測數值中心',
         '量測單位', '量測次數', '量具名稱']
        measure_item_data_old = measure_item_data
        print(measure_item_data_old[0])
        for item in measure_item_data_old:
            self.item = item.copy()
            self.measure_item_data.append(self.item)

        print(self.measure_item_data)
        self.ui.tableWidget_measure.setRowCount(len(self.measure_item))
        self.ui.tableWidget_measure.setColumnCount(len(self.measure_item_data))
        self.ui.tableWidget_measure.setVerticalHeaderLabels(self.measure_item)
        self.ui.tableWidget_measure.horizontalHeader().setVisible(False)
        print(len(self.measure_item), len(self.measure_item_data))
        for i in range(0, len(self.measure_item)):
            for i_2 in range(0, len(self.measure_item_data)):
                data = QTableWidgetItem(str(self.measure_item_data[i_2][i]))
                data.setTextAlignment(QtCore.Qt.AlignHCenter)
                data.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget_measure.setItem(i, i_2, data)

        self.ui.tableWidget_measure.setEditTriggers(QtWidgets.QTableWidget.DoubleClicked)
        print(len(self.measure_item) + int(self.measure_item_data[0][5]))
        self.ui.tableWidget_measure.setRowCount(len(self.measure_item) + int(self.measure_item_data[0][5]) * int(self.part_number))
        self.measure_number_list = list()
        for number in range(1, int(self.part_number) + 1):
            if int(self.measure_item_data[0][5]) > 1:
                for i in range(int(self.measure_item_data[0][5])):
                    self.measure_number_list.append('%s - %s' % (number, i + 1))

            elif int(self.measure_item_data[0][5]) == 1:
                self.measure_number_list.append('%s - 1' % number)

        self.ui.tableWidget_measure.resizeRowsToContents()
        self.ui.tableWidget_measure.setVerticalHeaderLabels(self.measure_item + self.measure_number_list)
        self.measure_image_item = self.sql.sql_all_image_item(self.project_name)
        self.ui.label_item_image.setPixmap(QtGui.QPixmap(BASE_DIR + '\\measure_item_image\\%s\\%s.jpg' % (self.project_name, self.measure_image_item[0])))
        self.ui.label_item_image.setScaledContents(True)
        self.ui.tableWidget_measure.doubleClicked.connect(self.double_clicked)
        self.ui.tableWidget_measure.cellChanged.connect(self.value_insert)
        self.ui.tableWidget_measure.itemSelectionChanged.connect(self.get_blank_form)
        self.tb.actionTriggered[QtWidgets.QAction].connect(self.tool_bar)
        self.statusBar().showMessage('開始量測')
        self.showMaximized()

    def tool_check(self, tool_name):
        print(tool_name)
        self.row = self.ui.tableWidget_measure.currentRow()
        print(self.row)
        print(int(self.row + self.number))
        tool_check = False
        for item in gvar.tool_data.keys():
            if tool_name == item:
                tool_check = True
                continue

        print(self.ui.tableWidget_measure.item(7, self.column).text())
        if tool_check == True:
            if str(self.ui.tableWidget_measure.item(7, self.column).text()) == gvar.tool_data[tool_name]:
                pass
            else:
                if self.ui.tableWidget_measure.item(7, self.column).text() != tool_name:
                    self.reply = QMessageBox.warning(self, '警示', '未使用正確無線量具', QMessageBox.Yes)
                    self.ui.tableWidget_measure.item(int(self.row + self.number), self.column).setText(' ')
        elif tool_check == False:
            self.reply = QMessageBox.warning(self, '警示', '量具名稱未在資料庫中', QMessageBox.Yes)
            self.ui.tableWidget_measure.item(self.row, self.column).setText('')

    def tool_bar(self, text):
        tool_bar = str(text.text())
        print('tool_bar模式%s' % tool_bar)
        if tool_bar == 'UP project':
            print('上傳資料')
            self.window = date_updata_window(self.measure_value_data, self.measure_item_data, self.part_number)
            self.window.show()
        else:
            if tool_bar == 'project_item':
                print(self.project_name)
                self.window = measure_project_show(self.project_name)
                self.window.show()
            else:
                if tool_bar == 'project_choose':
                    self.window = tool_measure_choose()
                    self.window.show()
                elif tool_bar == 'part_affect':
                    row = self.ui.tableWidget_measure.currentRow()
                    print(self.measure_number_list[(row - 7)])
                    part_number = list(self.measure_number_list[(row - 7)])[0]
                    self.window = appearance_affect_image_insert(part_number)
                    self.window.show()

    def unit_check(self, unit):
        print(unit)
        if str(unit) != str(self.ui.tableWidget_measure.item(4, self.column).text()):
            self.reply = QMessageBox.warning(self, '警示', '量測單位錯誤', QMessageBox.Yes)

    def drawing(self, drawing_data, drawing_upper, drawing_lower):
        drawing_new_data = []
        drawing_value = []
        drawing_upper_list = []
        drawing_lower_list = []
        drawing_number = []
        for item in self.measure_number_list:
            for item_2 in drawing_data:
                try:
                    if item_2[7] == item:
                        drawing_new_data.append(item_2)
                except:
                    pass

        for i in range(0, len(drawing_new_data)):
            drawing_upper_list.append(float(drawing_upper))
            drawing_lower_list.append(float(drawing_lower))

        for item in drawing_new_data:
            drawing_number.append(item[7])
            drawing_value.append(float(item[0]))

        plt.cla()
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.xlabel('量測次數')
        plt.ylabel('量測數值')
        plt.title('量測數據')
        plt.scatter(drawing_number, drawing_value, marker='o', c='brown')
        plt.plot(drawing_number, drawing_upper_list, label='上限')
        plt.plot(drawing_number, drawing_lower_list, label='下限')
        plt.legend()
        self.ui.canvas.draw()

    def double_clicked(self):
        self.row = self.ui.tableWidget_measure.currentRow()
        self.column = self.ui.tableWidget_measure.currentColumn()

    def value_insert(self):
        print('偷看')
        try:
            self.ui.tableWidget_measure.disconnect()
            self.measure_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime())
            self.row = self.ui.tableWidget_measure.currentRow()
            self.colunm = self.ui.tableWidget_measure.currentColumn()
            self.insert_value = self.ui.tableWidget_measure.item(self.row, self.colunm).text()
            try:
                test = float(self.insert_value)
                self.gonogo = measure.measure_go_nogo_calculate(float(self.ui.tableWidget_measure.item(1, self.column).text()), float(self.ui.tableWidget_measure.item(2, self.column).text()), float(self.insert_value))
                self.ui.tableWidget_project_item.setItem(0, 0, QTableWidgetItem(str(self.ui.tableWidget_measure.item(0, self.column).text())))
                if self.gonogo == True:
                    self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\GO.PNG'))
                    self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('GO'))
                    self.ui.tableWidget_measure.item(self.row, self.column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.ui.tableWidget_measure.item(self.row, self.column).setForeground(QtGui.QBrush(QtGui.QColor('black')))
                elif self.gonogo == False:
                    self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\NOGO.PNG'))
                    self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('NOGO'))
                    self.ui.tableWidget_measure.item(self.row, self.column).setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    self.ui.tableWidget_measure.item(self.row, self.column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.ui.tableWidget_project_item.setItem(0, 1, QTableWidgetItem(self.measure_time))
                print(self.measure_number_list)
                self.measure_value_new_data = [self.insert_value,
                     self.ui.tableWidget_measure.item(4, self.column).text(),
                     self.measure_time,
                     self.ui.tableWidget_measure.item(1, self.column).text(),
                     self.ui.tableWidget_measure.item(2, self.column).text(),
                     self.ui.tableWidget_measure.item(5, self.column).text(),
                     self.ui.tableWidget_measure.item(0, self.column).text(),
                     self.measure_number_list[int(self.row - 7)],
                     self.ui.tableWidget_measure.item(6, self.column).text(),
                     self.measurer]
                if len(self.measure_value_data) > 0:
                    self.measure_value_data_check = True
                    self.delet_data = []
                    for item in self.measure_value_data:
                        if item[7] == self.measure_value_new_data[7]:
                            if item[6] == self.measure_value_new_data[6]:
                                print(self.measure_value_data.index(item))
                                self.delet_data = item[:]
                                self.measure_value_data_check = False
                            else:
                                if not item[7] != self.measure_value_new_data[7]:
                                    if item[6] != self.measure_value_new_data[6]:
                                        pass

                    if self.measure_value_data_check == False:
                            dele_number = self.measure_value_data.index(self.delet_data)
                            self.measure_value_data.remove(self.delet_data)
                            print('刪除:%s' % self.delet_data)
                            self.measure_value_data.insert(dele_number, self.measure_value_new_data)
                    else:
                            if self.measure_value_data_check is True:
                                self.measure_value_data.append(self.measure_value_new_data)
                elif len(self.measure_value_data) == 0:
                        self.measure_value_data.append(self.measure_value_new_data)
                print('all_data :%s' % self.measure_value_data)
                for item in self.measure_value_data:
                    if item[6] == self.ui.tableWidget_measure.item(0, self.column).text():
                        self.measure_yield.append(item[0])

                value_excellent, value_inferior, all = measure.measure_Yield(float(self.ui.tableWidget_measure.item(1, self.column).text()), float(self.ui.tableWidget_measure.item(2, self.column).text()), self.measure_yield)
                self.ui.tableWidget_project_item.setItem(0, 3, QTableWidgetItem(str(value_excellent)))
                self.ui.tableWidget_project_item.setItem(0, 4, QTableWidgetItem(str(value_inferior)))
                self.ui.tableWidget_project_item.setItem(0, 5, QTableWidgetItem(str(all)))
                self.ui.tableWidget_project_item.setItem(0, 2, QTableWidgetItem(str(self.ui.tableWidget_measure.item(6, self.column).text())))
                self.measure_yield.clear()
                drawing_data = []
                for item in self.measure_value_data:
                    if item[6] == self.ui.tableWidget_measure.item(0, self.column).text():
                        drawing_data.append(item)

                drawing_upper = self.ui.tableWidget_measure.item(1, self.column).text()
                drawing_lower = self.ui.tableWidget_measure.item(2, self.column).text()
                self.drawing(drawing_data, drawing_upper, drawing_lower)
            except:
                self.dele_item_number = self.measure_number_list[(self.row - 7)]
                self.dele_item_measure_item = self.measure_item_data[self.column][0]
                for i in self.measure_value_data:
                    if i[6] == self.dele_item_measure_item and i[7] == self.dele_item_number:
                        self.measure_value_data.remove(i)
                        print('刪除%s' % i)

                self.reply = QMessageBox.question(self, '警示', '請輸入數字?', QMessageBox.Yes)
                self.ui.tableWidget_measure.setItem(self.row, self.column, QTableWidgetItem(''))
                drawing_data = []
                for item in self.measure_value_data:
                    if item[6] == self.ui.tableWidget_measure.item(0, self.column).text():
                        drawing_data.append(item)

                drawing_upper = self.ui.tableWidget_measure.item(1, self.column).text()
                drawing_lower = self.ui.tableWidget_measure.item(2, self.column).text()
                self.drawing(drawing_data, drawing_upper, drawing_lower)

        except:
            print('未輸入資料')

        self.ui.tableWidget_measure.doubleClicked.connect(self.double_clicked)
        self.ui.tableWidget_measure.cellChanged.connect(self.value_insert)
        self.ui.tableWidget_measure.itemSelectionChanged.connect(self.get_blank_form)
        data = []
        self.measure_ok_part = []
        now_measure_part = list(self.measure_number_list[int(self.row - 7)])[0]
        print(now_measure_part)
        for number in range(1, int(self.part_number) + 1):
            number_is_insert = False
            for value in self.measure_value_data:
                if list(value[7])[0] == str(number):
                    data.append(value)

            one_part_measure_value_len = len(self.measure_item_data) * self.measure_item_data[0][5]
            if int(one_part_measure_value_len) == len(data):
                if now_measure_part == str(number):
                    print('%s_measure_ok' % number)
                    for item in gvar.appearance_affect_all_data:
                        if item['number'] == number:
                            number_is_insert = True

                    if number_is_insert is True:
                        pass
                    else:
                        self.measure_ok_part.append(number)
                        self.window = appearance_affect_image_insert(number)
                        self.window.show()
            data = []

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter:
            print('enter')

    def drawing_plot(self):
        pass

    def setmeasurevalue(self, value):
        self.ui.tableWidget_measure.disconnect()
        if len(self.measure_value_data) == len(self.measure_item_data) * int(self.part_number) * int(self.measure_item_data[0][(-2)]):
            print('measure_over')
            self.reply = QMessageBox.question(self, '警示', '已完成量測', QMessageBox.Yes)
            self.ui.tableWidget_measure.doubleClicked.connect(self.double_clicked)
            self.ui.tableWidget_measure.cellChanged.connect(self.value_insert)
            self.ui.tableWidget_measure.itemSelectionChanged.connect(self.get_blank_form)
        else:
            if self.measure_number_list[(-1)] == self.measure_number_list[(self.row - 8)] and len(self.measure_value_data) != len(self.measure_item_data) * int(self.part_number) * int(self.measure_item_data[0][(-2)]) and self.row != self.ui.tableWidget_measure.currentRow() and self.change is True:
                print('measure_not_over')
                self.reply = QMessageBox.question(self, '警示', '未完成量測.-.', QMessageBox.Yes)
                self.ui.tableWidget_measure.doubleClicked.connect(self.double_clicked)
                self.ui.tableWidget_measure.cellChanged.connect(self.value_insert)
                self.ui.tableWidget_measure.itemSelectionChanged.connect(self.get_blank_form)
            else:
                if gvar.measure_type == '依照件數':
                    self.measure_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime())
                    self.value = value
                    if self.row != self.ui.tableWidget_measure.currentRow() or self.row is None:
                        self.number = 0
                    else:
                        if self.column != self.ui.tableWidget_measure.currentColumn() or self.column is None:
                            self.number = 0
                    self.row = self.ui.tableWidget_measure.currentRow()
                    self.column = self.ui.tableWidget_measure.currentColumn()
                    self.ui.tableWidget_measure.setItem(self.row + self.number, self.column, QTableWidgetItem(str(self.value)))
                    self.gonogo = measure.measure_go_nogo_calculate(float(self.ui.tableWidget_measure.item(1, self.column).text()), float(self.ui.tableWidget_measure.item(2, self.column).text()), float(self.value))
                    self.ui.tableWidget_project_item.setItem(0, 0, QTableWidgetItem(str(self.ui.tableWidget_measure.item(0, self.column).text())))
                    if self.gonogo == True:
                        self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\GO.PNG'))
                        self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('GO'))
                        self.ui.tableWidget_measure.item(self.row + self.number, self.column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    else:
                        if self.gonogo == False:
                            self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\NOGO.PNG'))
                            self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('NOGO'))
                            self.ui.tableWidget_measure.item(self.row + self.number, self.column).setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                            self.ui.tableWidget_measure.item(self.row + self.number, self.column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                        self.measure_value_new_data = [
                         self.value,
                         self.ui.tableWidget_measure.item(4, self.column).text(),
                         self.measure_time,
                         self.ui.tableWidget_measure.item(1, self.column).text(),
                         self.ui.tableWidget_measure.item(2, self.column).text(),
                         self.ui.tableWidget_measure.item(5, self.column).text(),
                         self.ui.tableWidget_measure.item(0, self.column).text(),
                         self.measure_number_list[(self.row + self.number - 7)],
                         self.ui.tableWidget_measure.item(6, self.column).text(),
                         self.measurer]
                        if len(self.measure_value_data) > 0:
                            self.delet_data = []
                            for item in self.measure_value_data:
                                if item[7] == self.measure_value_new_data[7]:
                                    if item[6] == self.measure_value_new_data[6]:
                                        self.delet_data = item[:]
                                        self.measure_value_data_check = False
                                    else:
                                        if item[7] != self.measure_value_new_data[7] or item[6] != self.measure_value_new_data[6]:
                                            self.measure_value_data_check = True

                            if self.measure_value_data_check is False:
                                dele_number = self.measure_value_data.index(self.delet_data)
                                self.measure_value_data.remove(self.delet_data)
                                self.measure_value_data.insert(dele_number, self.measure_value_new_data)
                                print('清除資料:%s' % self.delet_data)
                            if self.delet_data != []:
                                if self.measure_value_data_check == True:
                                    dele_number = self.measure_value_data.index(self.delet_data)
                                    self.measure_value_data.remove(self.delet_data)
                                    self.measure_value_data.insert(dele_number, self.measure_value_new_data)
                                    print('清除資料:%s' % self.delet_data)
                            if self.measure_value_data_check is True:
                                self.find_number_check = False
                                if self.find_number_check is True:
                                    print('Ture')
                                else:
                                    if self.find_number_check is False:
                                        self.measure_value_data.append(self.measure_value_new_data)
                                print('新增資料:%s' % self.measure_value_new_data)
                        elif len(self.measure_value_data) == 0:
                            self.measure_value_data.append(self.measure_value_new_data)
                    self.number = self.number + 1
                    for item in self.measure_value_data:
                        if item[6] == self.ui.tableWidget_measure.item(0, self.column).text():
                            self.measure_yield.append(item[0])

                    value_excellent, value_inferior, all = measure.measure_Yield(float(self.ui.tableWidget_measure.item(1, self.column).text()), float(self.ui.tableWidget_measure.item(2, self.column).text()), self.measure_yield)
                    self.ui.tableWidget_project_item.setItem(0, 3, QTableWidgetItem(str(value_excellent)))
                    self.ui.tableWidget_project_item.setItem(0, 4, QTableWidgetItem(str(value_inferior)))
                    self.ui.tableWidget_project_item.setItem(0, 5, QTableWidgetItem(str(all)))
                    self.ui.tableWidget_project_item.setItem(0, 2, QTableWidgetItem(str(self.ui.tableWidget_measure.item(6, self.column).text())))
                    self.measure_yield.clear()
                    self.ui.tableWidget_measure.doubleClicked.connect(self.double_clicked)
                    self.ui.tableWidget_measure.cellChanged.connect(self.value_insert)
                    self.ui.tableWidget_measure.itemSelectionChanged.connect(self.get_blank_form)
                    drawing_data = []
                    for item in self.measure_value_data:
                        if item[6] == self.ui.tableWidget_measure.item(0, self.column).text():
                            drawing_data.append(item)

                    drawing_upper = self.ui.tableWidget_measure.item(1, self.column).text()
                    drawing_lower = self.ui.tableWidget_measure.item(2, self.column).text()
                    self.drawing(drawing_data, drawing_upper, drawing_lower)
                elif gvar.measure_type == '零件部位':
                    self.measure_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime())
                    self.value = value
                    self.ui.label_item_image.setPixmap(QtGui.QPixmap(BASE_DIR + '\\measure_item_image\\%s\\%s.jpg' % (
                     self.project_name, str(self.ui.tableWidget_measure.item(0, self.column).text().split(' - ')[0]))))
                    self.ui.tableWidget_measure.setItem(self.row, self.column, QTableWidgetItem(str(self.value)))
                    self.gonogo = measure.measure_go_nogo_calculate(float(self.ui.tableWidget_measure.item(1, self.column).text()), float(self.ui.tableWidget_measure.item(2, self.column).text()), float(self.value))
                    self.ui.tableWidget_project_item.setItem(0, 0, QTableWidgetItem(str(self.ui.tableWidget_measure.item(0, self.column).text())))
                    if self.gonogo == True:
                        self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\GO.PNG'))
                        self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('GO'))
                        self.ui.tableWidget_measure.item(self.row, self.column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    else:
                        if self.gonogo == False:
                            self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\NOGO.PNG'))
                            self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('NOGO'))
                            self.ui.tableWidget_measure.item(self.row, self.column).setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                            self.ui.tableWidget_measure.item(self.row, self.column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                        self.measure_value_new_data = [
                         self.value,
                         self.ui.tableWidget_measure.item(4, self.column).text(),
                         self.measure_time,
                         self.ui.tableWidget_measure.item(1, self.column).text(),
                         self.ui.tableWidget_measure.item(2, self.column).text(),
                         self.ui.tableWidget_measure.item(5, self.column).text(),
                         self.ui.tableWidget_measure.item(0, self.column).text(),
                         self.measure_number_list[(self.row - 7)],
                         self.ui.tableWidget_measure.item(6, self.column).text(),
                         self.measurer]
                        if len(self.measure_value_data) > 0:
                            self.delet_data = []
                            for item in self.measure_value_data:
                                if item[7] == self.measure_value_new_data[7]:
                                    if item[6] == self.measure_value_new_data[6]:
                                        self.delet_data = item[:]
                                        self.measure_value_data_check = False
                                    else:
                                        if item[7] != self.measure_value_new_data[7] or item[6] != self.measure_value_new_data[6]:
                                            self.measure_value_data_check = True

                            if self.measure_value_data_check is False:
                                dele_number = self.measure_value_data.index(self.delet_data)
                                self.measure_value_data.remove(self.delet_data)
                                self.measure_value_data.insert(dele_number, self.measure_value_new_data)
                                print('清除資料:%s' % self.delet_data)
                            if self.delet_data != []:
                                if self.measure_value_data_check == True:
                                    dele_number = self.measure_value_data.index(self.delet_data)
                                    self.measure_value_data.remove(self.delet_data)
                                    self.measure_value_data.insert(dele_number, self.measure_value_new_data)
                                    print('清除資料:%s' % self.delet_data)
                            if self.measure_value_data_check is True:
                                self.find_number_check = False
                                if self.find_number_check is True:
                                    print('Ture')
                                else:
                                    if self.find_number_check is False:
                                        self.measure_value_data.append(self.measure_value_new_data)
                                print('新增資料:%s' % self.measure_value_new_data)
                        elif len(self.measure_value_data) == 0:
                            self.measure_value_data.append(self.measure_value_new_data)
                    for item in self.measure_value_data:
                        if item[6] == self.ui.tableWidget_measure.item(0, self.column).text():
                            self.measure_yield.append(item[0])

                    value_excellent, value_inferior, all = measure.measure_Yield(float(self.ui.tableWidget_measure.item(1, self.column).text()), float(self.ui.tableWidget_measure.item(2, self.column).text()), self.measure_yield)
                    self.ui.tableWidget_project_item.setItem(0, 3, QTableWidgetItem(str(value_excellent)))
                    self.ui.tableWidget_project_item.setItem(0, 4, QTableWidgetItem(str(value_inferior)))
                    self.ui.tableWidget_project_item.setItem(0, 5, QTableWidgetItem(str(all)))
                    self.ui.tableWidget_project_item.setItem(0, 2, QTableWidgetItem(str(self.ui.tableWidget_measure.item(6, self.column).text())))
                    self.measure_yield.clear()
                    drawing_data = []
                    for item in self.measure_value_data:
                        if item[6] == self.ui.tableWidget_measure.item(0, self.column).text():
                            drawing_data.append(item)

                    drawing_upper = self.ui.tableWidget_measure.item(1, self.column).text()
                    drawing_lower = self.ui.tableWidget_measure.item(2, self.column).text()
                    self.drawing(drawing_data, drawing_upper, drawing_lower)
                    item = self.measure_number_list[(self.row - 7)]
                    if list(self.measure_number_list[(self.row - 7)])[(-1)] == self.measure_item_data[0][(-2)]:
                        if self.measure_item_data[(-1)][0] != self.ui.tableWidget_measure.item(0, self.column).text():
                            print('換部位')
                            self.row = self.row - int(self.measure_item_data[0][(-2)]) + 1
                            self.column = self.column + 1
                            self.change = False
                    if int(list(self.measure_number_list[(self.row - 7)])[(-1)]) < int(self.measure_item_data[0][(-2)]):
                        print('往下')
                        self.row = int(self.row) + 1
                        self.change = False
                    else:
                        if list(self.measure_number_list[(self.row - 7)])[(-1)] == self.measure_item_data[0][(-2)]:
                            if self.measure_item_data[(-1)][0] == self.ui.tableWidget_measure.item(0, self.column).text():
                                data = []
                                self.measure_ok_part = []
                                now_measure_part = list(self.measure_number_list[int(self.row - 7)])[0]
                                print(now_measure_part)
                                for number in range(1, int(self.part_number) + 1):
                                    number_is_insert = False
                                    for value in self.measure_value_data:
                                        if list(value[7])[0] == str(number):
                                            data.append(value)

                                    one_part_measure_value_len = len(self.measure_item_data) * int(self.measure_item_data[0][5])
                                    if int(one_part_measure_value_len) == len(data):
                                        if now_measure_part == str(number):
                                            print('%s_measure_ok' % number)
                                            for item in gvar.appearance_affect_all_data:
                                                if item['number'] == number:
                                                    number_is_insert = True

                                            if number_is_insert is True:
                                                pass
                                            else:
                                                self.measure_ok_part.append(number)
                                                self.window = appearance_affect_image_insert(number)
                                                self.window.show()
                                    data = []

                                self.row = int(self.row) + 1
                                self.column = 0
                                print('換零件')
                                self.change = True
                        print('all_data=%s' % self.measure_value_data)
                        self.ui.tableWidget_measure.doubleClicked.connect(self.double_clicked)
                        self.ui.tableWidget_measure.cellChanged.connect(self.value_insert)
                        self.ui.tableWidget_measure.itemSelectionChanged.connect(self.get_blank_form)

    def measure_tool_start(self):
        self.measure_value.is_on = True
        self.measure_value.set_port(gvar.system_com_name)
        self.measure_value.start()

    def closeEvent(self, QCloseEvent):
        self.reply = QMessageBox.question(self, '警示', '確定離開量測頁面?', QMessageBox.Yes, QMessageBox.No)
        if self.reply == QMessageBox.Yes:
            self.hide()
            self.window = TOOLWindow()
            self.window.show()
        elif self.reply == QMessageBox.No:
            QCloseEvent.ignore()

    def get_blank_form(self):
        self.ui.tableWidget_measure.disconnect()
        print('查看')
        column = self.ui.tableWidget_measure.currentColumn()
        row = self.ui.tableWidget_measure.currentRow()
        self.row = int(row)
        self.column = int(column)
        try:
            self.value = float(self.ui.tableWidget_measure.item(row, column).text())
            value_check = True
            if row < 7:
                value_check = False
        except:
            value_check = False

        self.ui.label_item_image.setPixmap(QtGui.QPixmap(BASE_DIR + '\\measure_item_image\\%s\\%s.jpg' % (
         self.project_name, str(self.ui.tableWidget_measure.item(0, column).text().split(' - ')[0]))))
        self.ui.label_project_item_name.setText('量測項目：%s' % str(self.ui.tableWidget_measure.item(0, column).text().split(' - ')[0]))
        for item in self.measure_value_data:
            if item[6] == self.ui.tableWidget_measure.item(0, column).text():
                self.measure_yield.append(float(item[0]))

        print(self.measure_yield)
        value_excellent, value_inferior, all = measure.measure_Yield(float(self.ui.tableWidget_measure.item(1, self.column).text()), float(self.ui.tableWidget_measure.item(2, self.column).text()), self.measure_yield)
        self.measure_yield.clear()
        self.ui.tableWidget_project_item.setItem(0, 3, QTableWidgetItem(str(value_excellent)))
        self.ui.tableWidget_project_item.setItem(0, 4, QTableWidgetItem(str(value_inferior)))
        self.ui.tableWidget_project_item.setItem(0, 5, QTableWidgetItem(str(all)))
        if value_check is True:
            self.gonogo = measure.measure_go_nogo_calculate(float(self.ui.tableWidget_measure.item(1, column).text()), float(self.ui.tableWidget_measure.item(2, column).text()), float(self.value))
            if self.gonogo == True:
                self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\GO.PNG'))
                self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('GO'))
                self.ui.tableWidget_measure.item(row, column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.ui.tableWidget_measure.item(row, column).setForeground(QtGui.QBrush(QtGui.QColor('black')))
            elif self.gonogo == False:
                self.ui.label_gonogo.setPixmap(QtGui.QPixmap(BASE_DIR + '\\NOGO.PNG'))
                self.ui.tableWidget_project_item.setItem(0, 6, QTableWidgetItem('NOGO'))
                self.ui.tableWidget_measure.item(row, column).setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                self.ui.tableWidget_measure.item(row, column).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if value_check is True:
            self.ui.tableWidget_project_item.setItem(0, 0, QTableWidgetItem(self.ui.tableWidget_measure.item(0, column).text()))
            for item in self.measure_value_data:
                if item[7] == self.measure_number_list[int(row - 8)] and item[6] == self.ui.tableWidget_measure.item(0, column).text():
                    print(item)
                    self.ui.tableWidget_project_item.setItem(0, 1, QTableWidgetItem(item[2]))

            drawing_data = []
            for item in self.measure_value_data:
                if item[6] == self.ui.tableWidget_measure.item(0, column).text():
                    drawing_data.append(item)

            drawing_upper = self.ui.tableWidget_measure.item(1, column).text()
            drawing_lower = self.ui.tableWidget_measure.item(2, column).text()
            self.drawing(drawing_data, drawing_upper, drawing_lower)
        self.ui.tableWidget_measure.doubleClicked.connect(self.double_clicked)
        self.ui.tableWidget_measure.cellChanged.connect(self.value_insert)
        self.ui.tableWidget_measure.itemSelectionChanged.connect(self.get_blank_form)


class tool_measure_choose(QtWidgets.QWidget, Ui_check):
    measure_mode = pyqtSignal(str)

    def __init__(self):
        super(tool_measure_choose, self).__init__()
        self.ui = Ui_check()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.ui.pushButton_exit.clicked.connect(self.close)
        self.ui.radioButton.clicked.connect(self.mode_show)
        self.ui.radioButton_2.clicked.connect(self.mode_show)
        self.ui.pushButton_setup.clicked.connect(self.mode_set_ok)

    def mode_show(self):
        rad = self.sender()
        if rad.text() == '依照零件部位':
            self.mode = '零件部位'
            gvar.measure_type = '零件部位'
        else:
            if rad.text() == '依照件數':
                self.mode = '依照件數'
                gvar.measure_type = '依照件數'
        print('視窗%s' % self.mode)

    def mode_set_ok(self):
        mode = self.mode
        self.measure_mode.emit(mode)
        self.close()

    def close(self):
        self.hide()


class measure_project_show(QtWidgets.QWidget, measure_show_project):

    def __init__(self, project_name):
        super(measure_project_show, self).__init__()
        self.ui = measure_show_project()
        self.ui.setupUi(self)
        self.showMaximized()
        self.sql = sql_connect.sql_connect()
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.project_name_item = ['專案名稱', '建立日期', '建立人', '材料', '機台', '批號', '備註', '班別', '零件圖']
        self.ui.tableWidget_project.setRowCount(1)
        self.ui.tableWidget_project.setColumnCount(len(self.project_name_item))
        self.ui.tableWidget_project.setHorizontalHeaderLabels(self.project_name_item)
        self.ui.tableWidget_project.verticalHeader().setVisible(False)
        self.work_order_id = self.sql.sql_work_order_id(gvar.work_order)
        self.measure_item_data = self.sql.sql_work_order_measure_item(self.work_order_id)
        self.work_order = self.sql.sql_work_order_sor_no_data(self.work_order_id)
        self.project_data = self.sql.sql_find_project(project_name)
        print(self.project_data)
        for i in range(0, len(self.project_data[0])):
            self.ui.tableWidget_project.setItem(0, i, QTableWidgetItem(str(self.project_data[0][i])))

        self.ui.tableWidget_project.resizeRowsToContents()
        self.ui.tableWidget_project.resizeColumnsToContents()
        print(project_name)
        print(self.measure_item_data)
        self.work_order_item = ['專案名稱', '工單', '件數', '備註', '建立日期']
        self.ui.tableWidget_work_order.setRowCount(1)
        self.ui.tableWidget_work_order.setColumnCount(len(self.work_order_item))
        self.ui.tableWidget_work_order.setHorizontalHeaderLabels(self.work_order_item)
        self.ui.tableWidget_work_order.verticalHeader().setVisible(False)
        for i_2 in range(0, len(self.work_order[0])):
            self.ui.tableWidget_work_order.setItem(0, i_2, QTableWidgetItem(str(self.work_order[0][i_2])))

        self.ui.tableWidget_work_order.resizeColumnsToContents()
        self.ui.tableWidget_work_order.resizeRowsToContents()
        self.measure_item = ['量測專案名稱', '量測項目名稱', '量測數值上限', '量測數值下限', '量測數值中心', '量測小數點位數', '量測單位', '量測點數', '量測次數',
         '量具名稱', '量測部位圖']
        self.ui.tableWidget_measure_items.setRowCount(len(self.measure_item_data))
        self.ui.tableWidget_measure_items.setColumnCount(len(self.measure_item))
        self.ui.tableWidget_measure_items.setHorizontalHeaderLabels(self.measure_item)
        self.ui.tableWidget_measure_items.verticalHeader().setVisible(False)
        for i in range(0, len(self.measure_item_data)):
            for item in range(0, len(self.measure_item_data[i])):
                self.ui.tableWidget_measure_items.setItem(i, item, QTableWidgetItem(str(self.measure_item_data[i][item])))

        self.ui.tableWidget_measure_items.resizeRowsToContents()
        self.ui.tableWidget_measure_items.resizeRowsToContents()
        self.ui.tableWidget_measure_items.setSelectionBehavior(self.ui.tableWidget_measure_items.SelectRows)
        self.image_item = []
        for item in self.measure_item_data:
            self.image_item.append(item[1])

        for item in self.image_item:
            icon = QTableWidgetItem(QtGui.QIcon(BASE_DIR + '\\measure_item_image\\%s\\%s.jpg' % (str(project_name), str(item))), '')
            print(self.image_item.index(item))
            self.ui.tableWidget_measure_items.setItem(self.image_item.index(item), 10, icon)
            self.ui.tableWidget_measure_items.setIconSize(QtCore.QSize(300, 300))
            self.ui.tableWidget_measure_items.setColumnWidth(10, 300)
            self.ui.tableWidget_measure_items.setRowHeight(self.image_item.index(item), 300)


class date_updata_window(QtWidgets.QWidget, data_check):

    def __init__(self, measure_data, measure_item, part_number):
        super(date_updata_window, self).__init__()
        self.project_name = str()
        self.ui = data_check()
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.update)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.pushButton_delet_image.clicked.connect(self.button_delet_data_appearance_defect)
        self.ui.pushButton_insert_image.clicked.connect(self.button_defect_insert)
        self.ui.pushButton_image.clicked.connect(self.button_image)
        self.measure_data = measure_data
        self.measure_item = measure_item
        self.measure_item_title = []
        number_list = []
        self.filename = ''
        for i in range(1, int(part_number) + 1):
            number_list.append(str(i))

        self.ui.comboBox.addItems(number_list)
        data = []
        self.len_data = []
        for item in measure_item:
            self.measure_item_title.append(item[0])

        self.ui.tableWidget.setRowCount(len(self.measure_item_title))
        self.ui.tableWidget.setColumnCount(1)
        self.ui.tableWidget.setVerticalHeaderLabels(self.measure_item_title)
        for i in self.measure_item:
            for i_2 in self.measure_data:
                if i[0] == i_2[6]:
                    data.append(i)

            number = len(data)
            if number != 0:
                print(self.measure_item.index(i))
                self.ui.tableWidget.setItem(self.measure_item.index(i), 0, QTableWidgetItem(str(len(data))))
                self.ui.tableWidget.item(self.measure_item.index(i), 0).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            else:
                if number == 0:
                    self.ui.tableWidget.setItem(self.measure_item.index(i), 0, QTableWidgetItem('沒有數據'))
                    self.ui.tableWidget.item(self.measure_item.index(i), 0).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            data = []

        self.insert_appearance_effect_table(gvar.appearance_affect_all_data)

    def close(self):
        self.hide()

    def update(self):
        self.measure_value_insert()
        self.hide()

    def button_image(self):
        self.filename, self.filetype = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.ui.label_image.setText(self.filename)
        print(self.filename)

    def insert_appearance_effect_table(self, all):
        self.ui.tableWidget_part.setRowCount(len(all))
        for i in range(0, len(all)):
            item = all[i]
            self.ui.tableWidget_part.setItem(i, 0, QTableWidgetItem(str(item['number'])))
            self.ui.tableWidget_part.setItem(i, 2, QTableWidgetItem(str(item['remake'])))
            icon = QTableWidgetItem(QtGui.QIcon(item['file_name']), '')
            self.ui.tableWidget_part.setItem(i, 1, icon)
            self.ui.tableWidget_part.setIconSize(QtCore.QSize(300, 300))
            self.ui.tableWidget_part.setColumnWidth(1, 300)
            self.ui.tableWidget_part.setRowHeight(i, 300)

        self.ui.lineEdit_remake.clear()
        self.filename = ''
        self.ui.label_image.setText('圖片路徑')
        self.ui.tableWidget_part.resizeColumnsToContents()
        self.ui.tableWidget_part.resizeRowsToContents()
        self.ui.tableWidget_part.setSelectionBehavior(self.ui.tableWidget_part.SelectRows)

    def appearance_effect_data_check(self, data):
        check = False
        if self.appearance_effect_data_all == []:
            pass
        else:
            if self.appearance_effect_data_all != []:
                for item in self.appearance_effect_data_all:
                    if item['number'] == data['number']:
                        check = True

            return check

    def button_defect_insert(self):
        data = {}
        if self.filename is None or self.filename == '':
            self.reply = QMessageBox.question(self, '警示', '請輸入圖片路徑Q', QMessageBox.Yes)
        elif self.image_to_base64_data(self.filename) is not None:
            remake = self.ui.lineEdit_remake.text()
            number = self.ui.comboBox.currentText()
            image_base64 = self.image_to_base64_data(self.filename)
            data = {'number':number,  'remake':remake,  'file_name':self.filename,  'image_base64':image_base64}
            gvar.appearance_affect_all_data.append(data)
            self.insert_appearance_effect_table(gvar.appearance_affect_all_data)

    def button_delet_data_appearance_defect(self):
        self.row = self.ui.tableWidget_part.currentRow()
        if self.row == '':
            print(self.row)
        else:
            remake = self.ui.tableWidget_part.item(self.row, 2).text()
            number = self.ui.tableWidget_part.item(self.row, 0).text()
            for item in gvar.appearance_affect_all_data:
                if str(item['number']) == number and item['remake'] == remake:
                    gvar.appearance_affect_all_data.remove(item)

        self.insert_appearance_effect_table(gvar.appearance_affect_all_data)

    def image_to_base64_data(self, img_path):
        import base64
        with open(img_path, 'rb') as (f):
            image_data = f.read()
            base64_data = base64.b64encode(image_data)
            base64_data = str(base64_data, 'utf-8')
        return base64_data

    def measure_value_insert(self):
        if self.measure_data == []:
            self.reply = QMessageBox.question(self, '警示', '量測數值數量為零不可上傳 \n 請量測完後再將數值上傳', QMessageBox.Yes)
        elif self.measure_data != []:
            self.check_len = []
            for item in self.measure_item:
                self.data_check = []
                for value in self.measure_data:
                    if item[0] == value[6]:
                        self.data_check.append(value)

                self.check_len.append(self.data_check)

            self.check = True
            for item in self.check_len:
                for item_2 in self.check_len:
                    if len(item) != len(item_2):
                        self.check = False
                        continue

            if self.check is True:
                sql = sql_connect.sql_connect()
                sql.sql_insert_value(self.measure_data)
                sql.sql_update_work_order_state(gvar.work_order)
                if gvar.appearance_affect_all_data == []:
                    pass
                else:
                    sql.sql_work_order_appearance_defect(gvar.work_order, gvar.appearance_affect_all_data)
                print('updata ok')
                self.reply = QMessageBox.question(self, '訊息', '量測數值已上傳', QMessageBox.Yes)
            elif self.check is False:
                self.reply = QMessageBox.question(self, '錯誤', '量測次數不同請確認再上傳!!!', QMessageBox.Yes)
                print('no insert')


class project_check_window(QtWidgets.QWidget, Ui_widget_projectcheck):

    def __init__(self, data_all, tool_ok_com):
        super(project_check_window, self).__init__()
        self.project_name = str()
        self.tool_com = tool_ok_com
        self.sql_project_data = data_all
        self.ui = Ui_widget_projectcheck()
        self.sql = sql_connect.sql_connect()
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.ui.setupUi(self)
        self.ui.pushButton_close.clicked.connect(self.close)
        self.ui.pushButton_cinfirm_project.clicked.connect(self.open_start_measure_window)
        self.ui.pushButton_rest_project.clicked.connect(self.resst_project)
        self.measure_check = False
        self.project_name_item = [
         '專案名稱', '建立日期', '建立人', '備註']
        self.ui.tableWidget_project.setRowCount(len(self.sql_project_data))
        self.ui.tableWidget_project.setColumnCount(len(self.project_name_item))
        self.ui.tableWidget_project.setHorizontalHeaderLabels(self.project_name_item)
        for i in range(len(self.sql_project_data)):
            for i_2 in range(0, len(self.sql_project_data[i])):
                self.ui.tableWidget_project.setItem(i, i_2, QTableWidgetItem(str(self.sql_project_data[i][i_2])))

        self.ui.tableWidget_project.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget_project.resizeColumnsToContents()
        self.ui.tableWidget_project.resizeRowsToContents()
        self.ui.tableWidget_project.setSelectionBehavior(self.ui.tableWidget_project.SelectRows)
        self.ui.tableWidget_project.itemClicked.connect(self.set_work_order_measure_item)
        self.ui.tableWidget_work_order.itemClicked.connect(self.work_order_set_measure_item)
        DIRT_TEMP = create_temp()
        self.measure_image_project = self.sql.sql_image_all_project_name()
        print(self.measure_image_project)
        for name in self.measure_image_project:
            measure_item = self.sql.sql_all_image_item('%s' % name)
            os.makedirs(BASE_DIR + '\\measure_item_image\\%s' % name)
            for item in measure_item:
                data = self.sql.sql_image_base64data(item)
                sql_connect.save('measure_item_image/%s/%s' % (name, item), data, 'jpg')
                print('load image ok')

    def set_work_order_measure_item(self, item):
        self.ui.lineEdit_work_order_selet.clear()
        print('選擇專案名稱:%s' % self.sql_project_data[item.row()][0])
        porject_name = self.sql_project_data[item.row()][0]
        self.ui.lineEdit_now_project_name.setText(self.sql_project_data[item.row()][0])
        self.work_order_item = [
         '工單', '件數', '建立時間', '備註']
        sql = sql_connect.sql_connect()
        print(self.sql_project_data[item.row()][0])
        self.work_order_data = sql.sql_find_work_order_all(str(self.sql_project_data[item.row()][0]))
        print(self.work_order_data)
        self.project_name = self.ui.lineEdit_now_project_name.text()
        self.ui.tableWidget_work_order.setRowCount(len(self.work_order_data))
        self.ui.tableWidget_work_order.setColumnCount(len(self.work_order_item))
        self.ui.tableWidget_work_order.setHorizontalHeaderLabels(self.work_order_item)
        self.ui.tableWidget_work_order.verticalHeader().setVisible(False)
        for i in range(len(self.work_order_data)):
            for i_2 in range(0, len(self.work_order_data[i])):
                self.ui.tableWidget_work_order.setItem(i, i_2, QTableWidgetItem(str(self.work_order_data[i][i_2])))

        self.ui.tableWidget_work_order.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget_work_order.resizeColumnsToContents()
        self.ui.tableWidget_work_order.resizeRowsToContents()
        self.ui.tableWidget_work_order.setSelectionBehavior(self.ui.tableWidget_work_order.SelectRows)
        self.measure_image_project = self.sql.sql_image_all_project_name()

    def work_order_set_measure_item(self, item):
        sql = sql_connect.sql_connect()
        print('選擇工單名稱:%s' % self.work_order_data[item.row()][0])
        gvar.work_order = self.work_order_data[item.row()][0]
        self.ui.lineEdit_work_order_selet.setText(self.work_order_data[item.row()][0])
        self.measure_item = ['量測項目名稱', '量測數值上限', '量測數值下限', '量測數值中心', '量測單位', '量測次數',
         '量具名稱', '量測部位圖']
        self.work_order_id = sql.sql_work_order_id(self.work_order_data[item.row()][0])
        self.measure_item_data = sql.sql_work_order_measure_item(self.work_order_id)
        self.ui.tableWidget_measureitem.setRowCount(len(self.measure_item_data))
        self.ui.tableWidget_measureitem.setColumnCount(len(self.measure_item))
        self.ui.tableWidget_measureitem.setHorizontalHeaderLabels(self.measure_item)
        for i in range(len(self.measure_item_data)):
            for i_2 in range(len(self.measure_item_data[i])):
                self.ui.tableWidget_measureitem.setItem(i, i_2, QTableWidgetItem(str(self.measure_item_data[i][i_2])))
                self.ui.tableWidget_measureitem.item(i, i_2).setTextAlignment(QtCore.Qt.AlignCenter)

        self.ui.tableWidget_measureitem.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget_measureitem.resizeColumnsToContents()
        self.ui.tableWidget_measureitem.resizeRowsToContents()
        self.ui.tableWidget_measureitem.setSelectionBehavior(self.ui.tableWidget_measureitem.SelectRows)
        project_id = sql.sql_work_order_get_project_id(self.work_order_id)
        project_name = sql.sql_project_name(project_id)
        self.image_item = []
        for item in self.measure_item_data:
            self.image_item.append(item[0])

        for item in self.image_item:
            icon = QTableWidgetItem(QtGui.QIcon(BASE_DIR + '\\measure_item_image\\%s\\%s.jpg' % (str(project_name), str(item))), '')
            print(self.image_item.index(item))
            self.ui.tableWidget_measureitem.setItem(self.image_item.index(item), 7, icon)
            self.ui.tableWidget_measureitem.setIconSize(QtCore.QSize(300, 300))
            self.ui.tableWidget_measureitem.setColumnWidth(7, 300)
            self.ui.tableWidget_measureitem.setRowHeight(self.image_item.index(item), 300)

        try:
            if len(self.measure_item_data) == 0:
                self.measure_check = False
            else:
                self.measure_check = True
        except:
            pass

    def resst_project(self):
        self.ui.tableWidget_project.clear()
        self.ui.tableWidget_project.setEditTriggers(QAbstractItemView.CurrentChanged)
        sql = sql_connect.sql_connect()
        self.sql_project_data = sql.sql_all_date('mysite_project')
        self.ui.tableWidget_project.setRowCount(len(self.sql_project_data))
        self.ui.tableWidget_project.setColumnCount(len(self.project_name_item))
        self.ui.tableWidget_project.setHorizontalHeaderLabels(self.project_name_item)
        for i in range(len(self.sql_project_data)):
            for i_2 in range(0, len(self.sql_project_data[i])):
                self.ui.tableWidget_project.setItem(i, i_2, QTableWidgetItem(str(self.sql_project_data[i][i_2])))

        self.ui.tableWidget_project.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget_project.resizeRowsToContents()

    def close(self):
        self.hide()
        self.window = TOOLWindow()
        self.window.show()

    def closeEvent(self, QCloseEvent):
        self.hide()
        self.window = TOOLWindow()
        self.window.show()

    def open_start_measure_window(self, QCloseEvent):
        self.measurer = self.ui.lineEdit_measure_staff.text()
        if self.measure_check == True:
            if self.measurer is not '':
                self.hide()
                print(self.ui.lineEdit_now_project_name.text())
                sql = sql_connect.sql_connect()
                self.window = MainWindow(self.project_name, self.measure_item_data, self.work_order_data, self.measurer)
                self.window.show()
            elif self.measurer is '':
                self.reply = QMessageBox.question(self, 'Message', '量測人員名稱未設定', QMessageBox.Yes)
        elif self.measure_check == False:
            self.reply = QMessageBox.question(self, 'Message', '量測專案沒有工單以及量測設定', QMessageBox.Yes)


class TOOLWindow(QtWidgets.QWidget, Ui_Form):
    com_signal = pyqtSignal(str)

    def __init__(self):
        super(TOOLWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.ui.tool_test.clicked.connect(self.open_tool_test)
        self.ui.start_measure.clicked.connect(self.open_porject_check_window)
        self.ui.excit.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.ui.syste_setting.clicked.connect(self.system_set)
        self.main_window_center()
        self.set_ok_con = None

    def system_set(self):
        self.hide()
        self.window = system_set()
        self.window.show()
        print('system_set')

    def main_window_center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def open_porject_check_window(self):
        from urllib import request, error

        def internet_on():
            try:
                request.urlopen('http://www.google.com', timeout=1)
                return True
            except error.URLError as err:
                return False

        get_internet_stat = internet_on()
        if self.set_ok_con is None:
            self.reply = QMessageBox.question(self, '警示', '量測量具還未設定', QMessageBox.Yes)
        if get_internet_stat is False:
            self.reply = QMessageBox.warning(self, '警示', '沒有網路連線', QMessageBox.Yes)
        elif self.set_ok_con is not None:
            if get_internet_stat is True:
                self.hide()
                sql = sql_connect.sql_connect()
                self.window = project_check_window(sql.sql_all_date('mysite_project'), self.set_ok_con)
                self.window.show()

    def send_com_signal(self):
        com = self.set_ok_con
        self.com_signal.emit(com)

    def open_tool_test(self):
        self.window = tool_test(toolconnect.com2())
        self.window.mysignal.connect(self.get_signal)
        self.window.show()

    def closeEvent(self, QCloseEvent):
        self.reply = QMessageBox.question(self, '警示', '確定離開量測系統?', QMessageBox.Yes, QMessageBox.No)
        if self.reply == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

    def get_signal(self, con):
        self.set_ok_con = con
        print(self.set_ok_con)


class system_set(QtWidgets.QWidget, Ui_Form_system_set):

    def __init__(self):
        super(system_set, self).__init__()
        self.ui = Ui_Form_system_set()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.data_reply()
        self.ui.sql_reset_button_2.clicked.connect(self.reset_sql_data)
        self.ui.sql_reply_button_2.clicked.connect(self.reply_sql_data)
        self.ui.sql_set_button.clicked.connect(self.set_sql_data)
        self.ui.pushButton_create_tool.clicked.connect(self.tool_create)

    def tool_create(self):
        print('tool_create')
        self.window = system_tool_create()
        self.window.show()

    def data_reply(self):
        gvar.system_data = read_json.read_data(gvar.system_json)
        print(gvar.system_data)
        try:
            self.ui.lineEdit_host.setText(gvar.system_data['sql']['host'])
            self.ui.lineEdit_name.setText(gvar.system_data['sql']['name'])
            self.ui.lineEdit_user.setText(gvar.system_data['sql']['user'])
            self.ui.lineEdit_charset.setText(gvar.system_data['sql']['charset'])
            self.ui.lineEdit_password.setText(gvar.system_data['sql']['password'])
        except:
            pass

    def reset_sql_data(self):
        print('reset_sql_data')
        self.ui.lineEdit_host.clear()
        self.ui.lineEdit_name.clear()
        self.ui.lineEdit_user.clear()
        self.ui.lineEdit_charset.clear()
        self.ui.lineEdit_password.clear()
        for item in gvar.system_data['sql']:
            gvar.system_data['sql'][item] = ''

    def reply_sql_data(self):
        print('reply_data')
        data = read_json.read_data(gvar.system_json)
        self.ui.lineEdit_host.setText(data['sql']['host'])
        self.ui.lineEdit_name.setText(data['sql']['name'])
        self.ui.lineEdit_user.setText(data['sql']['user'])
        self.ui.lineEdit_charset.setText(data['sql']['charset'])
        self.ui.lineEdit_password.setText(data['sql']['password'])

    def set_sql_data(self):
        print('set_sql_data')
        data = read_json.read_data(gvar.system_json)
        if self.ui.lineEdit_host.text() != '':
            if self.ui.lineEdit_user.text() != '':
                if self.ui.lineEdit_name.text() != '':
                    if self.ui.lineEdit_charset.text() != '':
                        if self.ui.lineEdit_password.text() != '':
                            if data['sql'] != gvar.system_data['sql']:
                                gvar.system_data['sql']['host'] = self.ui.lineEdit_host.text()
                                gvar.system_data['sql']['user'] = self.ui.lineEdit_user.text()
                                gvar.system_data['sql']['name'] = self.ui.lineEdit_name.text()
                                gvar.system_data['sql']['charset'] = self.ui.lineEdit_charset.text()
                                gvar.system_data['sql']['password'] = self.ui.lineEdit_password.text()
                                print(gvar.system_data)
        else:
            self.reply = QMessageBox.question(self, '警示', 'SQL未設置完成', QMessageBox.Yes)


class system_tool_create(QtWidgets.QWidget, tool_create):

    def __init__(self):
        super(system_tool_create, self).__init__()
        self.ui = tool_create()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.ui.pushButton_measure_tool_create.clicked.connect(self.insert_tool_name)

    def insert_tool_name(self):
        print('insert_tool_name')
        self.tool_name = self.ui.lineEdit_create_tool.text()
        print(self.tool_name)
        self.ui.lineEdit_create_tool.clear()

    def insert_table_tool_name(self):
        data = read_json.read_data(gvar.system_json)
        self.measure_tool_name = data['measure_tool']['measure_tool_name']


class appearance_affect_image_insert(QtWidgets.QWidget, appearance_affect):

    def __init__(self, number):
        super(appearance_affect_image_insert, self).__init__()
        self.ui = appearance_affect()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico.ico'))
        self.ui.label_part_number.setText(str(number))
        self.part_number = number
        self.ui.pushButton.clicked.connect(self.button_image_file)
        self.ui.pushButton_insert.clicked.connect(self.button_insert)
        self.ui.pushButton_delet.clicked.connect(self.button_delet)
        self.appearance_affect_item = ['零件編號', '外觀圖片', '備註']
        self.ui.tableWidget_appearnance_affect.setColumnCount(len(self.appearance_affect_item))
        self.ui.tableWidget_appearnance_affect.setHorizontalHeaderLabels(self.appearance_affect_item)
        self.appearance_affect_all_data = []
        for item in gvar.appearance_affect_all_data:
            if str(self.part_number) == str(item['number']):
                self.appearance_affect_all_data.append(item)

        self.appearance_affect_table_update()

    def button_image_file(self):
        self.file_name, self.file_type = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.ui.label_image_url.setText(self.file_name)

    def image_to_base64_data(self, img_path):
        import base64
        with open(img_path, 'rb') as (f):
            image_data = f.read()
            base64_data = base64.b64encode(image_data)
            base64_data = str(base64_data, 'utf-8')
        return base64_data

    def button_insert(self):
        if self.file_name == '':
            self.reply = QMessageBox.question(self, '訊息', '未選擇圖片.-.', QMessageBox.Yes)
        else:
            self.remake = self.ui.textEdit_remake.toPlainText()
            image_base64 = self.image_to_base64_data(self.file_name)
            data = {'number':self.part_number,  'remake':self.remake,  'file_name':self.file_name,
             'image_base64':image_base64}
            self.appearance_affect_all_data.append(data)
            gvar.appearance_affect_all_data.append(data)
            self.appearance_affect_table_update()
            self.reset_input()
            self.file_name = ''
            self.remake = ''
            image_base64 = ''

    def button_delet(self):
        self.row = self.ui.tableWidget_appearnance_affect.currentRow()
        if self.row == '':
            print(self.row)
            self.reply = QMessageBox.question(self, '訊息', '選擇刪除項目拜託QAQ', QMessageBox.Yes)
        else:
            remake = self.ui.tableWidget_appearnance_affect.item(self.row, 2).text()
            number = self.ui.tableWidget_appearnance_affect.item(self.row, 0).text()
            image_file = self.ui.tableWidget_appearnance_affect.item(self.row, 1).text()
            for item in self.appearance_affect_all_data:
                if str(item['number']) == number and item['remake'] == remake:
                    self.appearance_affect_all_data.remove(item)
                    gvar.appearance_affect_all_data.remove(item)

        self.appearance_affect_table_update()

    def reset_input(self):
        self.ui.label_image_url.setText('圖片路徑')
        self.ui.textEdit_remake.clear()

    def appearance_affect_table_update(self):
        self.ui.tableWidget_appearnance_affect.setRowCount(len(self.appearance_affect_all_data))
        for i in range(0, len(self.appearance_affect_all_data)):
            item = self.appearance_affect_all_data[i]
            print(item['number'])
            print(item['remake'])
            print(item['file_name'])
            self.ui.tableWidget_appearnance_affect.setItem(i, 2, QTableWidgetItem(item['remake']))
            self.ui.tableWidget_appearnance_affect.setItem(i, 0, QTableWidgetItem(str(item['number'])))
            icon = QTableWidgetItem(QtGui.QIcon(item['file_name']), '')
            self.ui.tableWidget_appearnance_affect.setItem(i, 1, icon)
            self.ui.tableWidget_appearnance_affect.setIconSize(QtCore.QSize(300, 300))
            self.ui.tableWidget_appearnance_affect.setColumnWidth(1, 300)
            self.ui.tableWidget_appearnance_affect.setRowHeight(i, 300)

        self.ui.tableWidget_appearnance_affect.resizeColumnsToContents()
        self.ui.tableWidget_appearnance_affect.resizeRowsToContents()
        self.ui.tableWidget_appearnance_affect.setSelectionBehavior(self.ui.tableWidget_appearnance_affect.SelectRows)

    def insert_line_text_reset(self):
        self.ui.textEdit_remake.clear()
        self.ui.label_image_url.setText('圖片路徑')


class tool_test(QtWidgets.QWidget, Ui_toolcheck):
    mysignal = pyqtSignal(str)

    def __init__(self, tool_com_all):
        self.tool_com_all = tool_com_all
        super(tool_test, self).__init__()
        self.ui = Ui_toolcheck()
        self.ui.setupUi(self)
        self.main_window_center()
        self.setWindowIcon(QtGui.QIcon(BASE_DIR + '\\ico_1.ico'))
        for com_obj in self.tool_com_all:
            self.ui.comboBox_comname.addItem(com_obj)

        self.measure_value = measure_thread()
        self.measure_value.measure_value.connect(self.setmeasurevalue)
        self.measure_value.measure_tool_name.connect(self.setmeasuretoolname)
        self.ui.Button_tool_connect.clicked.connect(self.measure_tooltest_start)
        self.ui.Button_tool_connect_rest.clicked.connect(self.tool_rest)
        self.ui.pushButton_9.clicked.connect(self.close)
        self.ui.pushButton_10.clicked.connect(self.tool_set_ok)
        self.chick_tool_ok = False

    def tool_set_ok(self):
        if self.chick_tool_ok == False:
            self.reply = QMessageBox.question(self, 'Message', '量測量具還未設定', QMessageBox.Yes)
        elif self.chick_tool_ok == True:
            self.measure_value.is_on = False
            self.con = self.set_con
            gvar.system_com_name = self.set_con
            self.mysignal.emit(self.con)
            self.hide()

    def tool_rest(self):
        self.chick_tool_ok = False
        self.ui.comboBox_comname.clear()
        rest_com_choose = toolconnect.com2()
        for com_obj in rest_com_choose:
            self.ui.comboBox_comname.addItem(com_obj)

        self.ui.lineEdit_toolname.setText(' ')
        self.ui.lineEdit_toolvalue.setText(' ')
        self.measure_value.is_on = False
        self.measure_value = measure_thread()
        self.measure_value.measure_value.connect(self.setmeasurevalue)
        self.measure_value.measure_tool_name.connect(self.setmeasuretoolname)
        print('self.measure_value.is_on=%s' % self.measure_value.is_on)

    def setmeasurevalue(self, value):
        self.ui.lineEdit_toolvalue.setText(value)

    def setmeasuretoolname(self, name):
        try:
            self.ui.lineEdit_toolname.setText(gvar.tool_data[name])
        except:
            self.reply = QMessageBox.warning(self, '警示', '無線量具名稱未在資料庫中', QMessageBox.Yes)

    def closeEvent(self, QCloseEvent):
        self.measure_value.is_on = False
        self.measure_value.wait()
        print('self.measure_value.is_on=%s' % self.measure_value.is_on)

    def main_window_center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def measure_tooltest_start(self):
        print(self.chick_tool_ok)
        print(self.ui.comboBox_comname.currentText())
        if self.chick_tool_ok:
            self.reply = QMessageBox.question(self, 'Message', '量具已設定完成', QMessageBox.Yes)
        if self.ui.comboBox_comname.currentText() == '':
            self.reply = QMessageBox.question(self, 'Message', '未選擇量具', QMessageBox.Yes)
        elif self.ui.comboBox_comname.currentText() != '':
            if self.chick_tool_ok == False:
                self.chick_tool_ok = True
                self.set_con = self.ui.comboBox_comname.currentText().split('-')[0]
                self.set_con = re.findall('-?\\d+\\.?\\d*', self.set_con)
                self.set_con = self.set_con[0]
                print('self.set_con=%s' % self.set_con[0])
                self.measure_value.is_on = True
                self.measure_value.set_port(self.set_con)
                self.measure_value.start()

    def close(self):
        self.hide()
        self.measure_value.is_on = False
        print('self.measure_value.is_on=%s' % self.measure_value.is_on)


class measure_thread(QThread):
    measure_value = pyqtSignal(str)
    measure_tool_name = pyqtSignal(str)
    measure_unit = pyqtSignal(str)

    def __init__(self, parent=None):
        super(measure_thread, self).__init__(parent)
        self.is_on = True

    def set_port(self, port):
        self.set_port = port

    def run(self):
        while self.is_on:
            returenlist = self.serial_test(self.set_port)
            if self.is_on == False:
                break
            self.measure_value.emit(str(returenlist[0]))
            self.measure_tool_name.emit(str(returenlist[1]))
            self.measure_unit.emit(str(returenlist[2]))

    def serial_test(self, comnumber):
        COM_PORT = 'COM%s' % comnumber
        BAUD_RATES = 57600
        BYTE_SIZE = 8
        PARITY = 'N'
        STOP_BITS = 1
        ser = serial.Serial(COM_PORT, BAUD_RATES, BYTE_SIZE, PARITY, STOP_BITS, timeout=None)
        string_slice_start = 8
        string_slice_period = 12
        try:
            while True:
                if self.is_on == False:
                    ser.close()
                    break
                while ser.in_waiting:
                    data_raw = ser.read_until(b'\r')
                    data = data_raw.decode()
                    equipment_ID = data[:string_slice_start - 1]
                    altered_string = data[string_slice_start:string_slice_start + string_slice_period - 1]
                    altered_int = float(altered_string)
                    unit = list(data)
                    I = 'I'
                    if unit[(-2)] == I:
                        altered_unit = 'in'
                    else:
                        altered_unit = 'mm'
                    a = []
                    a.append(altered_int)
                    a.append(equipment_ID)
                    a.append(altered_unit)
                    print(a)
                    ser.close()
                    return a

        except:
            pass


def create_temp():
    folder = os.path.exists(BASE_DIR + '\\measure_iteem_image')
    try:
        os.makedirs(BASE_DIR + '\\measure_item_image')
        print('建立目錄')
    except:
        path = BASE_DIR + '\\measure_item_image'
        try:
            shutil.rmtree(path)
            print('刪除資料夾')
        except:
            pass

        os.makedirs(BASE_DIR + '\\measure_item_image')
        print('建立目錄')


def delet():
    path = BASE_DIR + '\\measure_item_image'
    try:
        shutil.rmtree(path)
    except OSError as e:
        print(e)
    else:
        print('刪除資料夾')


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    DIRT_TEMP = create_temp()
    app = QtWidgets.QApplication([])
    window = TOOLWindow()
    window.show()
    sys.exit(app.exec_())
# okay decompiling qt5test.pyc
