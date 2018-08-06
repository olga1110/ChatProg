# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'General_Form.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_General_Form(object):
    def setupUi(self, General_Form):
        General_Form.setObjectName("General_Form")
        General_Form.resize(668, 452)
        self.contacts_button = QtWidgets.QPushButton(General_Form)
        self.contacts_button.setGeometry(QtCore.QRect(130, 60, 451, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.contacts_button.setFont(font)
        self.contacts_button.setObjectName("contacts_button")
        self.chat_button = QtWidgets.QPushButton(General_Form)
        self.chat_button.setGeometry(QtCore.QRect(130, 200, 451, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.chat_button.setFont(font)
        self.chat_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("GUI/Img/messanger.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chat_button.setIcon(icon)
        self.chat_button.setIconSize(QtCore.QSize(1000, 300))
        self.chat_button.setObjectName("chat_button")

        self.retranslateUi(General_Form)
        QtCore.QMetaObject.connectSlotsByName(General_Form)

    def retranslateUi(self, General_Form):
        _translate = QtCore.QCoreApplication.translate
        General_Form.setWindowTitle(_translate("General_Form", "Form"))
        self.contacts_button.setText(_translate("General_Form", "Управление контактами"))

