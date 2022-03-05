import sys
import time
from decimal import Decimal
from os import path

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDir
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTableWidgetItem,
                             QLabel, QMessageBox, QFileDialog, QDialog)

import PDF2EXCEL
from IMPORT_DATA import ImportExceldata
from MainWindow import Ui_MainWindow
from sounding_table import Sounding_Cal


class QmyMainwindow(QMainWindow):
    """
    窗口程序实例显示
    """
    # 自定义信号
    currentcell_changed = pyqtSignal([int], [str])
    currentcell_changed_sum = pyqtSignal([int], [str])
    currentcell_changed_sum_weight = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.lineEdit_density.setText('0.98')
        self.ui.lineEdit_temperature.setText('25')
        self.ui.tableWidget.horizontalHeader().setDefaultSectionSize(88)  # 方法可行，设置固定列宽
        self.ui.tableWidget.verticalHeader().setDefaultSectionSize(40)  # 设置列高
        self.ui.tableWidget_2.verticalHeader().setDefaultSectionSize(10)
        # self.ui.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)   # 方法存在疑问
        self.label_erro = QLabel('错误类型:', self)
        self.ui.statusbar.addWidget(self.label_erro)
        self.flag = True
        while self.flag:
            if path.exists('sql.db'):
                self.flag = False
                self.set_tab_title()
                self.currentcell_changed.connect(self.setitem)
                self.currentcell_changed[str].connect(self.ualgauge_changed)
                self.currentcell_changed_sum[int].connect(self.volumn_sum)
                self.currentcell_changed_sum[str].connect(self.vol_changed)
                self.currentcell_changed_sum_weight[int].connect(self.weight_sum)
                continue
            else:
                self.messagebox = QMessageBox.information(self, '软件所在目录没有数据', '请导入仓容表！')
                # need to create additional Windows which contains import table function.
                # self.on_pushButton_import_tab_clicked()

            # QMetaObject.connectSlotsByName(self)

    # ============================定义槽函数=====================================

    @pyqtSlot(int, int)
    def on_tableWidget_cellChanged(self, row, column):
        """
        使用自定信号结合内置信号，定制新信号。某列单元内容改变，发射信号。
        :param row: tablewidget行
        :param column: tablewidget列
        """
        if self.ui.tableWidget.item(row, column) is None:
            pass
        elif self.ui.tableWidget.item(row, column).text() == '':
            pass
        elif self.ui.tableWidget.item(row, column).text().isalpha():
            pass
        else:
            rowcount = self.ui.tableWidget.rowCount()
            if column == 2:
                if row < rowcount - 5:
                    self.currentcell_changed[int].emit(row)
            elif column == 4:
                if row < rowcount - 5:
                    self.currentcell_changed[int].emit(row)
                if row > rowcount - 6:
                    self.currentcell_changed_sum[str].emit(str(row))
            # 空高计算实高，信号给出
            elif column == 3:
                if row < rowcount - 5:
                    self.currentcell_changed[str].emit(str(row))
            # 体积列求和信号
            elif column == 5:
                if row != rowcount - 1:
                    self.currentcell_changed_sum[int].emit(rowcount)
                if rowcount - 1 > row > rowcount - 6:
                    self.currentcell_changed_sum[str].emit(str(row))
            # 质量列求和
            elif column == 6:
                if row != rowcount - 1:
                    self.currentcell_changed_sum_weight[int].emit(rowcount)

    @pyqtSlot(int)
    def volumn_sum(self, row_count):
        time.sleep(0.05)
        __sum = self.sum(row_count, 5)
        self.ui.tableWidget.setItem(row_count - 1, 5, QTableWidgetItem(str(__sum)))

    @pyqtSlot(str)
    def vol_changed(self, row):
        volumn = Decimal(self.ui.tableWidget.item(int(row), 5).text())
        weight = self.weight(int(row), volumn)
        self.ui.tableWidget.setItem(int(row), 6, QTableWidgetItem(weight))

    @pyqtSlot(int)
    def weight_sum(self, row_count):
        time.sleep(0.05)
        __sum = self.sum(row_count, 6)
        self.ui.tableWidget.setItem(row_count - 1, 6, QTableWidgetItem(str(__sum)))

    @pyqtSlot(str)
    def ualgauge_changed(self, row):
        row = int(row)
        total_height = float(self.ui.tableWidget.item(row, 1).text())
        print(total_height)
        if self.ui.tableWidget.item(row, 3) is None:
            ualgauge = float('0')
        else:
            if self.ui.tableWidget.item(row, 3).text() == '':
                ualgauge = float('0')
            else:
                ualgauge = float(self.ui.tableWidget.item(row, 3).text())
        if 0 <= ualgauge <= total_height:
            self.label_erro.setText('错误类型：无')
            item_row2 = total_height - ualgauge
            item = str(item_row2)
            print(item)
            print(type(item))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(item))
        else:
            self.label_erro.setText('错误类型：空高超出范围！')

    @pyqtSlot()
    def on_pushButton_INIT_OIL_STOR_clicked(self):
        self.ui.tableWidget_2.clearContents()

    @pyqtSlot()
    def on_pushButton_pdf2excel_clicked(self):
        current_path = QDir.currentPath()
        dlg_title = '选择需要导入的文件'
        filt = "所有文件(*.*);;pdf文件（*.pdf)"
        filename, filter_used = QFileDialog.getOpenFileName(self, dlg_title, current_path, filt)
        if filename:
            PDF2EXCEL.pdf2excel(filename)

    @pyqtSlot()  # 按钮clicked信号需要加上装饰器否则会导致槽函数的2次触发
    def on_pushButton_import_tab_clicked(self):
        current_path = QDir.currentPath()
        dlg_title = '选择需要导入的文件'
        filt = "所有文件(*.*);;Excel文件（*.xlsx)"
        filename, filter_used = QFileDialog.getOpenFileName(self, dlg_title, current_path, filt)
        if filename:
            ImportExceldata(filename)

    @pyqtSlot()
    def on_lineEdit_slot_editingFinished(self):
        """单行编辑框内容编辑完成后执行的槽函数"""
        v_header_text = Sounding_Cal('sql.db').table_names
        for i in range(len(v_header_text)):
            if self.ui.tableWidget.item(i, 2) is None:
                pass
            else:
                self.setitem(i)

    @pyqtSlot()
    def on_lineEdit_draft_editingFinished(self):
        print('ddd')
        self.on_lineEdit_slot_editingFinished()

    @pyqtSlot()
    def on_lineEdit_density_editingFinished(self):
        self.on_lineEdit_slot_editingFinished()

    @pyqtSlot()
    def on_lineEdit_temperature_editingFinished(self):
        self.on_lineEdit_slot_editingFinished()

    @pyqtSlot()
    def on_pushButton_data_excel_clicked(self):
        pass

    @pyqtSlot()
    def on_pushButton_filing_excel_clicked(self):
        pass

    @pyqtSlot()
    def on_tableWidget_data_excel_cellChanged(self):
        pass

    @pyqtSlot()
    def on_tableWidget_filling_excel_cellChanged(self):
        pass

    @pyqtSlot()
    def on_lineEdit_data_flag_editingFinished(self):
        # self.ui.lineEdit_data_flag.editingFinished.disconnect(self.on_lineEdit_data_flag_editingFinished)
        print('ddd')
        data_flag_column = self.ui.lineEdit_data_flag.text()
        if data_flag_column == '':
            QMessageBox.information(self, '错误！', '请填写标识列信息，如表中时间所在列序号。')
        # self.ui.lineEdit_data_flag.editingFinished.connect(self.on_lineEdit_data_flag_editingFinished)

    @pyqtSlot()
    def on_lineEdit_filing_flag_editingFinished(self):
        filing_flag_column = self.ui.lineEdit_filing_flag.text()
        if filing_flag_column == '':
            QMessageBox.information(QDialog(), '错误！', '请填写标识列信息，如表中时间所在列序号。', )

    # ============================定义槽函数=====================================

    # ============================tablewidget设置=====================================
    def set_tab_title(self):
        """
        设置tablewidget的水平表头和垂直表头,初始化item显示内容
        """
        v_header_text = Sounding_Cal(database='sql.db').table_names
        header_list = ['NO.1 SET.', 'NO.2 SET.', 'NO.1 SERV.', 'NO.2 SERV.', '总计']
        for i in header_list:
            v_header_text.append(i)
        # v_header_text.append('总计')
        h_header_text = ['总容积', '总高', '测高', '空高', '温度', '存油体积', '存油重量']
        h_count = len(h_header_text)
        v_count = len(v_header_text)
        self.ui.tableWidget.setRowCount(v_count)
        self.ui.tableWidget_2.setRowCount(v_count)
        self.ui.tableWidget.setColumnCount(h_count)
        self.ui.tableWidget_2.setColumnCount(2)
        # 初始化垂直表头
        for i in range(len(v_header_text)):
            v_header_item = QTableWidgetItem(v_header_text[i])
            self.ui.tableWidget.setVerticalHeaderItem(i, v_header_item)
            self.ui.tableWidget_2.setVerticalHeaderItem(i, v_header_item)

        # 初始化水平表头
        for i in range(len(h_header_text)):
            h_header_item = QTableWidgetItem(h_header_text[i])
            self.ui.tableWidget.setHorizontalHeaderItem(i, h_header_item)
            if i >= 5:
                self.ui.tableWidget_2.setHorizontalHeaderItem(i - 5, h_header_item)

        # 初始化总高显示
        for i in range(len(v_header_text) - 5):
            max_sounding = Sounding_Cal(database='sql.db').get_max_sounding(v_header_text[i], 'sound')
            print(max_sounding)
            item = QTableWidgetItem(str(max_sounding))
            self.ui.tableWidget.setItem(i, 1, item)
            # self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 初始化总容积
        for i in range(len(v_header_text) - 5):
            max_sounding = Sounding_Cal('sql.db').get_max_sounding(v_header_text[i], 'tr=0')
            print(max_sounding)
            item = QTableWidgetItem(str(max_sounding))
            self.ui.tableWidget.setItem(i, 0, item)
        # 初始化温度设置
        for i in range(len(v_header_text) - 1):
            self.ui.tableWidget.setItem(i, 4, QTableWidgetItem('25'))

    def ok_func(self, row, column):
        """
        返回查表计算结果
        :param row: UI界面table触发信号的行号，从0开始
        :param column: UI界面table触发信号的列号，从0开始
        :return: 有计算结果时返回计算结果，计算出现错误时返回错误内容
        """
        if self.ui.lineEdit_draft.text() == '':
            self.ui.lineEdit_draft.setText('0')
        if self.ui.lineEdit_slot.text() == '':
            self.ui.lineEdit_slot.setText('0')
        draft = self.ui.lineEdit_draft.text()
        slope = self.ui.lineEdit_slot.text()
        sounding = self.ui.tableWidget.item(row, column).text()
        table_name = self.ui.tableWidget.verticalHeaderItem(row).text()
        sounding_c = Sounding_Cal(draft=draft, slope=slope, sounding=sounding, oil_tank=table_name, database='sql.db')
        result = sounding_c.handling_result()
        return result

    def weight(self, row, result):
        if self.ui.lineEdit_density.text() == '':
            self.ui.lineEdit_density.setText('0.98')
        if self.ui.lineEdit_temperature.text() == '':
            self.ui.lineEdit_temperature.setText('25')
        density = self.ui.lineEdit_density.text()

        if self.ui.tableWidget.item(row, 4) is None:
            actual_density = Decimal(density)
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(self.ui.lineEdit_temperature.text()))
        elif self.ui.tableWidget.item(row, 4).text() == '':
            actual_density = Decimal(density)
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(self.ui.lineEdit_temperature.text()))
        else:
            actual_density = Decimal(density) - (Decimal(self.ui.tableWidget.item(row, 4).text()) -
                                                 Decimal(15)) * Decimal('0.00065')
        weight = str(Sounding_Cal('sql.db').round_dec(actual_density * Decimal(result), 3))
        return weight

    def sum(self, row_count, column):
        """
        返回查表计算结果
        :param row_count: 求和总行数
        :param column: 需要求和的列
        :return: 总和，decimal类型
        """
        __sum = Decimal('0')
        for i in range(row_count - 1):
            if self.ui.tableWidget.item(i, column) is None:
                text = '0'
            else:
                text = self.ui.tableWidget.item(i, column).text()
            if text == '':
                sum_i = Decimal('0')
            else:
                sum_i = Decimal(text)
            __sum += sum_i
        return __sum

    def setitem(self, row):
        """设置单元格显示计算结果"""

        result, flag = self.ok_func(row, 2)
        print(result)
        if flag:
            self.label_erro.setText('错误类型：无')
            item = str(Sounding_Cal('sql.db').round_dec(result, 3))
            weight = self.weight(row, result)
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(item))
            self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(weight))
        else:
            # draft=-2.8出错
            result_check = ''
            for i in result:
                result_check += i + ','
            print(1)
            self.label_erro.setText('错误类型：{}超出范围！'.format(result_check))
            # self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(result_check + '超出范围！'))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem('0'))
            self.ui.tableWidget.setItem(row, 6, QTableWidgetItem('0'))

    def voyage_abstract(self):
        pass


# ============================tablewidget设置=====================================


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyMainwindow()
    myWidget.show()
    sys.exit(app.exec_())
