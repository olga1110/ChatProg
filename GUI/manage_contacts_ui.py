# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manage_contacts.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(553, 485)
        self.create_chat_button = QtWidgets.QPushButton(Form)
        self.create_chat_button.setGeometry(QtCore.QRect(110, 40, 311, 81))
        self.create_chat_button.setObjectName("create_chat_button")
        self.add_contact_button = QtWidgets.QPushButton(Form)
        self.add_contact_button.setGeometry(QtCore.QRect(110, 240, 311, 81))
        self.add_contact_button.setObjectName("add_contact_button")
        self.del_contact_button = QtWidgets.QPushButton(Form)
        self.del_contact_button.setGeometry(QtCore.QRect(110, 340, 311, 81))
        self.del_contact_button.setObjectName("del_contact_button")
        self.show_contacts_button = QtWidgets.QPushButton(Form)
        self.show_contacts_button.setGeometry(QtCore.QRect(110, 140, 311, 81))
        self.show_contacts_button.setObjectName("show_contacts_button")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.create_chat_button.setText(_translate("Form", "Создать ЧАТ"))
        self.add_contact_button.setText(_translate("Form", "Добавить контакт"))
        self.del_contact_button.setText(_translate("Form", "Удалить контакт"))
        self.show_contacts_button.setText(_translate("Form", "Показать список контактов"))

