import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QLineEdit, QLabel, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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


class CMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.ui = ui_class()

        self.ui.setupUi(self)
        # self.ui.centralwidget.setContentsMargins(0, 0, 0, 0)
        # self.gridLayout = QtWidgets.QGridLayout()
        # self.gridLayout.setSpacing(0)
        # self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.ui.background_bt.setAutoFillBackground(True)
        self.ui.background_bt.setWindowOpacity(0.7)
        self.ui.centralwidget.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        icon = QtGui.QIcon()
        pixmap = QPixmap('GUI/Img/main.jpg')
        icon.addPixmap(pixmap)
        self.ui.background_bt.setIcon(icon)
        self.ui.background_bt.setContentsMargins(0, 0, 0, 0)
        # self.ui.background_bt.adjustSize()
        self.ui.enter_button.clicked.connect(self.get_login_input)
        button_style = 'QPushButton {background-color: #98B9DB; border: 1px solid #E32828; border-radius: 20px;}'
        self.ui.enter_button.setStyleSheet(button_style)
        self.ui.registr_button.clicked.connect(self.make_registr)
        self.ui.registr_button.setStyleSheet(button_style)
        self.ui.checkBox_registr.stateChanged.connect(self.show_registr)
        self.ui.online_RB.setChecked(True)
        self.ui.password.setEchoMode(QLineEdit.Password)
        self.ui.password_confirm.setEchoMode(QLineEdit.Password)
        self.ui.password_confirm.hide()
        self.ui.pass_confirm_label.hide()
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
            self.ui.password_confirm.show()
            self.ui.pass_confirm_label.show()
        else:
            self.ui.password_confirm.hide()
            self.ui.pass_confirm_label.hide()

    def make_registr(self):
        if self.ui.checkBox_registr.isChecked():
            login = self.ui.login_text.toPlainText()
            level = self.ui.level_combobox.currentText()
            password = self.ui.password.text()
            password1 = self.ui.password_confirm.text()
            result = self.s.get_register_response(login, level, password, password1)
            if result['response'] != 200:
                QMessageBox.warning(None, 'Warning', result['info'])
                return
            else:
                self.create_message_box(result['info'], 'Регистрация')
                self.ui.checkBox_registr.setChecked(False)
                self.ui.password.clear()

    def get_login_input(self):

        s = Client(addr, port)
        user_name = self.ui.login_text.toPlainText()
        level = self.ui.level_combobox.currentText()
        password = self.ui.password.text()
        if user_name == "":
            QMessageBox.warning(None, 'Warning', 'Не указан логин')
            return
        account_name = s.get_account_name(user_name)

        if self.ui.online_RB.isChecked():
            user_status = 'Y'
        else:
            user_status = 'N'
        # presence-сообщение и ответ сервера
        result = s.get_presence_response(account_name, user_status, level, password)
        if result['response'] == 202:
            # получить код сессии
            session = s.s.recv(1024).decode('utf-8')
            self.ui.general_form = CGeneralForm(s.s, account_name, level, session)
            self.ui.general_form.show()
        else:
            self.create_message_box(result['error'], 'Доступ запрещен')
        self.close()
        return account_name

    # def closeEvent(self, event):
    #
    #     reply = QMessageBox.question(self, 'Message', 'Выйти из ChatFree?',
    #                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #
    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()


class CGeneralForm(QtWidgets.QWidget):

    def __init__(self, sock, account_name, level, session, parent=None):

        super().__init__(parent)
        self.ui = ui_form()
        self.ui.setupUi(self)
        self.ui.sock = sock
        self.ui.account_name = account_name
        self.ui.level = level
        self.ui.session = session
        self.ui.background_bt.setAutoFillBackground(True)
        self.ui.background_bt.setWindowOpacity(0.7)
        # self.ui.General_Form.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        icon = QtGui.QIcon()
        pixmap = QPixmap('GUI/Img/menu.jpg')
        icon.addPixmap(pixmap)
        self.ui.background_bt.setIcon(icon)
        self.ui.background_bt.adjustSize()

        icon.addPixmap(QtGui.QPixmap("GUI/Img/settings.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.contacts_button.setIcon(icon)
        self.ui.contacts_button.setIconSize(QtCore.QSize(50, 50))

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("GUI/Img/chat.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.chat_button.setIcon(icon1)
        self.ui.chat_button.setIconSize(QtCore.QSize(50, 50))

        button_style = 'QPushButton {background-color: #98B9DB; border: 1px solid #E32828; border-radius: 20px;}'
        self.ui.contacts_button.setStyleSheet(button_style)
        self.ui.chat_button.setStyleSheet(button_style)
        self.list_contacts = ListContacts(sock)
        self.contacts = []

    def get_contacts(self):
        self.list_contacts.client_get_contacts(self.ui.session)
        count = self.list_contacts.read_server_response_contacts()
        for _ in range(count):
            server_response = self.list_contacts.read_server_response_contacts()
            self.contacts.append(server_response['user_id'])
        if self.contacts:
            return self.contacts
        return ['<Пусто>']

    def on_chat_button_pressed(self):
        self.contacts = self.get_contacts()
        self.ui.chat_form = CChatForm(self.ui.sock, self.ui.account_name, self.ui.level, self.ui.session,
                                      self.contacts)
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
