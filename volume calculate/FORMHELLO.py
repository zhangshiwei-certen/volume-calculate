# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FORMHELLO.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_FormHello(object):
    def setupUi(self, FormHello):  # FormHello 作为主窗体传入
        FormHello.setObjectName("FormHello")
        FormHello.resize(800, 600)
        self.Lab_hello = QtWidgets.QLabel(FormHello)
        self.Lab_hello.setGeometry(QtCore.QRect(120, 90, 181, 31))
        self.Lab_hello.setObjectName("Lab_hello")
        self.pushButton = QtWidgets.QPushButton(FormHello)
        self.pushButton.setGeometry(QtCore.QRect(160, 170, 93, 28))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(FormHello)
        QtCore.QMetaObject.connectSlotsByName(FormHello)

    def retranslateUi(self, FormHello):
        _translate = QtCore.QCoreApplication.translate
        FormHello.setWindowTitle(_translate("FormHello", "Form"))
        self.Lab_hello.setText(_translate("FormHello", "hello, by ui designer"))
        self.pushButton.setText(_translate("FormHello", "close"))
