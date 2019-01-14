# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chat.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(794, 542)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(0, 10, 431, 51))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 120, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.send_mes = QtWidgets.QTextEdit(Form)
        self.send_mes.setGeometry(QtCore.QRect(200, 100, 481, 71))
        self.send_mes.setObjectName("send_mes")
        self.send_button = QtWidgets.QPushButton(Form)
        self.send_button.setGeometry(QtCore.QRect(700, 100, 71, 71))
        self.send_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("GUI/Img/chat.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.send_button.setIcon(icon)
        self.send_button.setIconSize(QtCore.QSize(70, 70))
        self.send_button.setObjectName("send_button")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(20, 200, 55, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.chat_textBrowser = QtWidgets.QTextBrowser(Form)
        self.chat_textBrowser.setGeometry(QtCore.QRect(200, 200, 481, 231))
        self.chat_textBrowser.setObjectName("chat_textBrowser")
        self.exit_button = QtWidgets.QPushButton(Form)
        self.exit_button.setGeometry(QtCore.QRect(690, 480, 93, 41))
        self.exit_button.setObjectName("exit_button")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(500, 30, 131, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.user_textBrowser = QtWidgets.QTextBrowser(Form)
        self.user_textBrowser.setGeometry(QtCore.QRect(640, 20, 141, 31))
        self.user_textBrowser.setObjectName("user_textBrowser")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_2.setText(_translate("Form", "SIMPLE MESSANGER"))
        self.label.setText(_translate("Form", "Введите сообщение:"))
        self.label_4.setText(_translate("Form", "ЧАТ:"))
        self.exit_button.setText(_translate("Form", "ВЫХОД"))
        self.label_5.setText(_translate("Form", "Вход выполнен:"))

