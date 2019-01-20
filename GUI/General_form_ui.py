# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'General_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_General_Form(object):
    def setupUi(self, General_Form):
        General_Form.setObjectName("General_Form")
        General_Form.resize(405, 303)
        self.contacts_button = QtWidgets.QPushButton(General_Form)
        self.contacts_button.setGeometry(QtCore.QRect(50, -10, 291, 91))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.contacts_button.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Img/settings.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.contacts_button.setIcon(icon)
        self.contacts_button.setIconSize(QtCore.QSize(50, 50))
        self.contacts_button.setObjectName("contacts_button")
        self.background_bt = QtWidgets.QPushButton(General_Form)
        self.background_bt.setEnabled(True)
        self.background_bt.setGeometry(QtCore.QRect(0, 0, 412, 306))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.background_bt.sizePolicy().hasHeightForWidth())
        self.background_bt.setSizePolicy(sizePolicy)
        self.background_bt.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Img/menu.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.background_bt.setIcon(icon1)
        self.background_bt.setIconSize(QtCore.QSize(400, 300))
        self.background_bt.setShortcut("")
        self.background_bt.setAutoRepeatDelay(0)
        self.background_bt.setAutoRepeatInterval(0)
        self.background_bt.setObjectName("background_bt")
        self.chat_button = QtWidgets.QPushButton(General_Form)
        self.chat_button.setGeometry(QtCore.QRect(50, 220, 291, 91))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.chat_button.setFont(font)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("Img/chat.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chat_button.setIcon(icon2)
        self.chat_button.setIconSize(QtCore.QSize(50, 50))
        self.chat_button.setObjectName("chat_button")
        self.background_bt.raise_()
        self.contacts_button.raise_()
        self.chat_button.raise_()

        self.retranslateUi(General_Form)
        QtCore.QMetaObject.connectSlotsByName(General_Form)

    def retranslateUi(self, General_Form):
        _translate = QtCore.QCoreApplication.translate
        General_Form.setWindowTitle(_translate("General_Form", "Menu"))
        self.contacts_button.setText(_translate("General_Form", "Settings"))
        self.chat_button.setText(_translate("General_Form", "CHAT"))

