import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from Crypto.PublicKey import RSA
from GUI.messanger_ui import Ui_MainWindow as ui_class
from GUI.ChatForm import CChatForm
from GUI.General_form_ui import Ui_General_Form as ui_form
from GUI.ManageForm import CManageForm
from LIB.client import Client, Chat, ListContacts
from DB.DB_classes import *
from LIB.client_lib import *


# Параметры подключения клиента
try:
    addr = sys.argv[2]
except IndexError:
    addr = 'localhost'

try:
    port = int(sys.argv[3])
except IndexError:
    port = 7777
except ValueError:
    print('Задайте целочисленное значение для порта')
    sys.exit(0)

try:
    if sys.argv[1] in ('r', 'w'):
        mode = sys.argv[1]
except IndexError:
    # открываем по умолчанию на чтение
    mode = 'r'

if mode == 'w':
    mode_to_form = 'Запись'
else:
    mode_to_form = 'Чтение'


# Подключение к базе данных
engine = create_engine('sqlite:///clients_messages.db')
session = sessionmaker(bind=engine)()


class CMainWindow(QtWidgets.QMainWindow):

    def __init__(self, mode, parent=None):

        super().__init__(parent)

        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.mode = mode
        self.ui.mode_textBrowser.setText(mode)
        # self.error_dialog = QtWidgets.QErrorMessage()
        self.ui.enter_button.clicked.connect(self.get_login_input)
        self.ui.registr_button.clicked.connect(self.make_registr)
        self.ui.checkBox_registr.stateChanged.connect(self.show_registr)
        self.ui.password_text_1.hide()
        self.ui.pass1_label.hide()
        self.ui.level_combobox.addItem('1')
        self.ui.level_combobox.addItem('2')
        self.ui.level_combobox.addItem('3')
        self.s = Client(addr, port)

        # Генерируем пару ключей
        key = RSA.generate(1024)
        self.priv_key = key.exportKey('PEM')
        self.pub_key = key.publickey()

        # Отправляем открытый ключ серверу
        self.s.s.send(self.pub_key.exportKey(format='PEM', passphrase=None, pkcs=1))

    def create_message_box(self, text, title):
        ret = QtWidgets.QMessageBox.Ok
        m = QtWidgets.QMessageBox()
        m.setWindowTitle('Warning')
        m.setText(text)
        m.setWindowTitle(title)
        m.setIcon(QtWidgets.QMessageBox.Warning)
        m.setStandardButtons(QtWidgets.QMessageBox.Ok)
        m.adjustSize()
        ret = m.exec_()

    def show_registr(self, state):
        if state == Qt.Checked:
            self.ui.password_text_1.show()
            self.ui.pass1_label.show()
        else:
            self.ui.password_text_1.hide()
            self.ui.pass1_label.hide()

    def make_registr(self):
        if self.ui.checkBox_registr.isChecked():
            login = self.ui.login_text.toPlainText()
            level = self.ui.level_combobox.currentText()
            password = self.ui.password_text.toPlainText()
            password1 = self.ui.password_text_1.toPlainText()
            result = self.s.get_register_response(login, level, password, password1)
            print(result)
            if result['response'] != 200:
                QMessageBox.warning(None, 'Warning', result['info'])
                return
            else:
                self.create_message_box(result['info'], 'Регистрация')
                # self.ui.general_form = CGeneralForm(s.s, self.ui.mode, login)
                # self.ui.general_form.show()
                self.ui.checkBox_registr.setChecked(False)
                self.ui.password_text.clear()

    def get_login_input(self):

        s = Client(addr, port)
        user_name = self.ui.login_text.toPlainText()
        level = self.ui.level_combobox.currentText()
        password = self.ui.password_text.toPlainText()


        if user_name == "":
            QMessageBox.warning(None, 'Warning', 'Не указан логин')
            return

        account_name = s.get_account_name(user_name)
        user_status = s.get_user_status()
        # presense-сообщение и ответ сервера
        result = s.get_presense_response(account_name, user_status, level, password)
        if result['response'] == 202:
            # получить код сессии
            session = s.s.recv(1024).decode('utf-8')
            self.ui.general_form = CGeneralForm(s.s, self.ui.mode, account_name, level, session)
            self.ui.general_form.show()
        else:
            self.create_message_box('Login is incorrect!')
        return account_name


class CGeneralForm(QtWidgets.QWidget):

    def __init__(self, sock, mode, account_name, level, session, parent=None):

        super().__init__(parent)
        self.ui = ui_form()
        self.ui.setupUi(self)
        self.ui.mode = mode
        self.ui.sock = sock
        self.ui.account_name = account_name
        self.ui.level = level
        self.ui.session = session

    def on_chat_button_pressed(self):
        self.ui.chat_form = CChatForm(self.ui.sock, self.ui.mode, self.ui.account_name, self.ui.level, self.ui.session)
        self.ui.chat_form.show()

    def on_contacts_button_pressed(self):
        self.ui.manage_form = CManageForm(self.ui.sock, self.ui.mode, self.ui.account_name, self.ui.level, self.ui.session)
        self.ui.manage_form.show()


if __name__ == '__main__':

    # Запуск формы
    app = QtWidgets.QApplication(sys.argv)
    window = CMainWindow(mode_to_form)
    window.show()
    sys.exit(app.exec_())
















