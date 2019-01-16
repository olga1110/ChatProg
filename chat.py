import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from Crypto.PublicKey import RSA
from GUI.messenger_ui import Ui_MainWindow as ui_class
from GUI.ChatForm import CChatForm
from GUI.General_form_ui import Ui_General_Form as ui_form
from GUI.ManageForm import CManageForm
from LIB.client import Client, Chat, ListContacts
from DB.DB_classes import *


# Параметры подключения клиента
try:
    addr = sys.argv[1]
except IndexError:
    addr = 'localhost'

try:
    port = int(sys.argv[2])
except IndexError:
    port = 7777
except ValueError:
    print('Задайте целочисленное значение для порта')
    sys.exit(0)


# Подключение к базе данных
# engine = create_engine('sqlite:///clients_messages.db')
# session = sessionmaker(bind=engine)()


class CMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.enter_button.clicked.connect(self.get_login_input)
        self.ui.registr_button.clicked.connect(self.make_registr)
        self.ui.checkBox_registr.stateChanged.connect(self.show_registr)
        self.ui.online_RB.setChecked(True)
        self.ui.password_text_1.hide()
        self.ui.pass1_label.hide()
        self.ui.level_combobox.addItems(['1', '2', '3'])
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
            if result['response'] != 200:
                QMessageBox.warning(None, 'Warning', result['info'])
                return
            else:
                self.create_message_box(result['info'], 'Регистрация')
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

        if self.ui.online_RB.isChecked():
            user_status = 'Y'
        else:
            user_status = 'N'
        # presense-сообщение и ответ сервера
        result = s.get_presense_response(account_name, user_status, level, password)
        if result['response'] == 202:
            # получить код сессии
            session = s.s.recv(1024).decode('utf-8')
            self.ui.general_form = CGeneralForm(s.s, account_name, level, session)
            self.ui.general_form.show()
        else:
            self.create_message_box(result['error'], 'Доступ запрещен')
        return account_name

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message', 'Выйти из ChatFree?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class CGeneralForm(QtWidgets.QWidget):

    def __init__(self, sock, account_name, level, session, parent=None):

        super().__init__(parent)
        self.ui = ui_form()
        self.ui.setupUi(self)
        self.ui.sock = sock
        self.ui.account_name = account_name
        self.ui.level = level
        self.ui.session = session

    def on_chat_button_pressed(self):
        self.ui.chat_form = CChatForm(self.ui.sock, self.ui.account_name, self.ui.level, self.ui.session)
        self.ui.chat_form.show()

    def on_contacts_button_pressed(self):
        self.ui.manage_form = CManageForm(self.ui.sock, self.ui.account_name, self.ui.level, self.ui.session)
        self.ui.manage_form.show()


if __name__ == '__main__':

    # Запуск формы
    app = QtWidgets.QApplication(sys.argv)
    window = CMainWindow()
    window.show()
    sys.exit(app.exec_())
















