import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GUI.manage_contacts_ui import Ui_Form as manage_form
import LIB.client as client


class CManageForm(QtWidgets.QWidget):

    def __init__(self, sock, account_name, level, session, parent=None):
        super().__init__(parent)
        self.ui = manage_form()
        self.ui.setupUi(self)
        self.ui.sock = sock
        self.ui.account_name = account_name
        self.ui.level = level
        self.ui.session = session
        self.ui.show_contacts_button.clicked.connect(self.get_contacts)
        self.ui.add_contact_button.clicked.connect(self.add_contacts)
        self.ui.del_contact_button.clicked.connect(self.del_contacts)
        self.ui.create_chat_button.clicked.connect(self.create_chat)
        self.list_contacts = client.ListContacts(sock)
        # self._handler = Client.ClientHandler()

    def login_required(r_level):
        def decorator(func):
            def decorated2(self):
                f_level = int(self.ui.level)
                if r_level >= f_level:
                    # if kwargs['level'] == 1:
                    result = func(self)
                    return result
                else:
                    QMessageBox.warning(None, 'Warning',
                                        'Для выполнения данной операции необходим {}-й уровень доступа'.format(r_level))
                    return

            return decorated2

        return decorator

    def create_message_box(self, text, title):
        ret = QtWidgets.QMessageBox.Ok
        m = QtWidgets.QMessageBox()
        # m.resize(250,150)
        # m.setMinimumHeight(400)
        # m.setMinimumWidth(100)
        m.setText(text)
        m.layout()
        m.setWindowTitle(title)
        m.setStandardButtons(QtWidgets.QMessageBox.Ok)
        m.adjustSize()
        ret = m.exec_()

    @login_required(2)
    def get_contacts(self):
        self.list_contacts.client_get_contacts(self.ui.session)
        count = self.list_contacts.read_server_response_contacts()
        list = []
        for _ in range(count):
            server_response = self.list_contacts.read_server_response_contacts()
            list.append(server_response['user_id'])
        self.create_message_box('Ваш список контактов:\n{}'.format(str(list)), 'Список контактов')
        return list

    # Ваш список контактов:
    @login_required(1)
    def add_contacts(self):
        action = 'add_contact'
        nickname, ok = QtWidgets.QInputDialog.getText(self, 'Добавить контакт',
                                                      'Введите логин для добавления пользователя: ')

        while nickname == "":
            QMessageBox.warning(None, 'Warning', 'Не указан логин пользователя!')
            nickname, ok = QtWidgets.QInputDialog.getText(self, 'Добавить контакт',
                                                          'Введите логин для добавления пользователя: ')

        if ok:
            self.list_contacts.get_request_modify(action, nickname, self.ui.session)
            server_response_rcv = self.ui.sock.recv(4096)
            server_response = client.ClientHandler.message_decode(server_response_rcv)
            if server_response['response'] == 202:
                self.create_message_box('Операция выполнена успешно', 'Добавить контакт')
            else:
                self.create_message_box(server_response['error'], 'Добавить контакт')

    @login_required(1)
    def del_contacts(self):
        action = 'del_contact'
        nickname, ok = QtWidgets.QInputDialog.getText(self, 'Удалить контакт',
                                                      'Введите логин для удаления пользователя: ')
        while nickname == "":
            QMessageBox.warning(None, 'Warning', 'Не указан логин пользователя!')
            nickname, ok = QtWidgets.QInputDialog.getText(self, 'Удалить контакт',
                                                          'Введите логин для удаления пользователя: ')

        if ok:
            self.list_contacts.get_request_modify(action, nickname, self.ui.session)
            server_response_rcv = self.ui.sock.recv(4096)
            server_response = client.ClientHandler.message_decode(server_response_rcv)
            if server_response['response'] == 202:
                self.create_message_box('Операция выполнена успешно', 'Удалить контакт')
            else:
                self.create_message_box(server_response['error'], 'Удалить контакт')

    @login_required(2)
    def create_chat(self):
        users_id = []

        chat_name, ok = QtWidgets.QInputDialog.getText(self, 'Create',
                                                       'Задайте имя чата: ')
        if ok:
            while chat_name == "":
                QMessageBox.warning(None, 'Warning', 'Не указано имя чата!')
                chat_name, ok = QtWidgets.QInputDialog.getText(self, 'Создание чата',
                                                               'Задайте имя чата: ')
            add_user = 'Y'
            while add_user == 'Y':
                user_id, ok = QtWidgets.QInputDialog.getText(self, 'Create',
                                                             'Введите логин пользователя для добавления в чат: ')
                if ok:
                    while user_id == "":
                        QMessageBox.warning(None, 'Warning', 'Не указан логин пользователя!')
                        user_id, ok = QtWidgets.QInputDialog.getText(self, 'Create', 'Введите логин пользователя для '
                                                                                     'добавления в чат: ')

                    users_id.append(user_id)

                    reply = QMessageBox.question(self, 'Create', 'Продолжить добавление пользователей?',
                                                 QMessageBox.Yes | QMessageBox.No,
                                                 QMessageBox.No)

                    add_user = 'Y' if reply == QMessageBox.Yes else 'N'

                    self.list_contacts.create_chat(chat_name, users_id, self.ui.session)
                    server_response_rcv = self.ui.sock.recv(4096)
                    print(server_response_rcv)
                    server_response = client.ClientHandler.message_decode(server_response_rcv)
                    self.create_message_box('{}\n{}'.format(server_response['result'], server_response['error']),
                                            'Create')
                else:
                    return True
        else:
            # self.close()
            return True
