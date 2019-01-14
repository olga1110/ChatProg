import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GUI.chat_ui import Ui_Form as ui_chat
from LIB.client import Client, Chat



class ReadThread(QThread):
    in_msg = pyqtSignal(str) # сигнал который мы будем передавать прогрессбару
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.chat_client = Chat(sock)
        self.running = False
    def run(self):
        self.running = True
        while self.running:
            msg = self.chat_client.read_client_message()
            print(msg)
            if msg:
                self.in_msg.emit(msg)


class WriteThread(QThread):
    out_msg = pyqtSignal(str)  # сигнал который мы будем передавать прогрессбару

    def __init__(self, sock, msg, type_msg, to, login, session):
        super().__init__()
        self.sock = sock
        self.msg = msg
        self.type_msg = type_msg
        self.to = to
        self.login = login
        self.session = session
        self.chat_client = Chat(sock)
        self.running = False

    def run(self):
        self.running = True
        if self.type_msg == 'personal':
            self.chat_client.client_write_person(self.msg, self.to, self.login, self.session)
        else:
            self.chat_client.client_write_chat(self.msg, self.login, self.session)
        self.out_msg.emit(self.msg)


class CChatForm(QtWidgets.QWidget):
    incomeMessage = QtCore.pyqtSignal(str)
    def __init__(self, sock, account_name, level, session, parent=None):
        super().__init__(parent)
        self.ui = ui_chat()
        self.sock = sock
        self.ui.level = level
        self.ui.session = session
        # timer = QtCore.QTimer(self)
        # timer.start(3000)
        # timer.timeout.connect(self.read_message)
        self.ui.setupUi(self)
        self.ui.user_textBrowser.setText(account_name)
        self.ui.account_name = account_name
        self.ui.send_button.clicked.connect(self.write_message)
        self.ui.exit_button.clicked.connect(self.close)
        #self.chat_client = Chat(sock)

        self.thread = ReadThread(self.sock)
        self.thread.in_msg.connect(self.on_ReadThreadSignal)
        self.thread.start()

    def login_required(r_level):
        def decorator(func):
            def decorated2(self, *args):
                f_level = int(self.ui.level)
                if r_level >= f_level:
                    result = func(self, *args)
                    return result
                else:
                    QMessageBox.warning(None, 'Warning','Для выполнения данной операции необходим {}-й уровень доступа'.format(r_level))
                    return
            return decorated2
        return decorator

    # @login_required(3)
    # def read_message(self):
    #     msg = self.chat_client.read_client_message()
    #     print(msg)
    #     if msg:
    #         self.ui.chat_textBrowser.append(msg)

    @login_required(3)
    def write_message(self, sock):
        msg = self.ui.send_mes.toPlainText()

        if msg == "":
            QMessageBox.warning(None, 'Warning', 'Нельзя отправить пустое сообщение. Введите текст')
            return True
        reply = QMessageBox.question(self, 'System_question', 'Отправить сообщение в общий чат?', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            type_msg = 'chat'
            to = 'chat'
        else:
            type_msg = 'personal'
            to, _ = QtWidgets.QInputDialog.getText(self, 'System_question', 'Кому доставить сообщение? Введите логин: ')

        self.thread1 = WriteThread(self.sock, msg, type_msg, to, self.ui.account_name, self.ui.session)

        self.thread1.out_msg.connect(self.on_WriteThreadSignal)
        self.thread1.start()

    def on_WriteThreadSignal(self, value):
        self.ui.chat_textBrowser.append("<font color='red' > My message: {}</font>".format(value))
        self.ui.send_mes.clear()

    def on_ReadThreadSignal(self, value):
        self.ui.chat_textBrowser.append(value)

    # def close(self):
    #     self.thread.running = False
    #     self.close()
        #кнопка ВЫХОД

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Выйти из Чата?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()