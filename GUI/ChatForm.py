import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GUI.chat_ui import Ui_Form as ui_chat
from LIB.client import Client, Chat
import LIB.client_lib as client_lib




class CChatForm(QtWidgets.QWidget):
    incomeMessage = QtCore.pyqtSignal(str)
    def __init__(self, sock, mode, account_name, level, session, parent=None):
        super().__init__(parent)
        self.ui = ui_chat()
        self.ui.mode = mode
        self.ui.level = level
        self.ui.session = session
        # self.chat_textBrowser.incomeMessage.connect(self.read_message)
        # self.ui.chat_textBrowser.connect(self.get_msg_value)
        # self.connect(self.ui.chat_textBrowser, QtCore.SIGNAL())
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.read_message)


        self.ui.setupUi(self)
        self.ui.mode_textBrowser.setText(mode)
        self.ui.user_textBrowser.setText(account_name)
        self.ui.account_name = account_name
        # self.ui.chat_textBrowser.setText(self.read_message)
        self.ui.send_button.clicked.connect(self.write_message)
        # QtCore.QObject.connect(self.ui.chat_textBrowser, QtCore.SIGNAL("activated(const QString&)"),
        #                        self.read_message)
        self.chat_client = Chat(sock)
        self.timer.start(1000)

    # def on_changed_value(self, msg):
    #     # Активируем сигнал
    #     self.incomeMessage.emit(msg)
    #
    # # Создаём Qt-слот
    # @pyqtSlot(int)
    # def get_msg_value(self, msg):
    #     self.ui.chat_textBrowser.setText(msg)
    def login_required(r_level):
        def decorator(func):
            def decorated2(self):
                f_level = int(self.ui.level)
                if r_level >= f_level:
                    # if kwargs['level'] == 1:
                    result = func(self)
                    return result
                else:
                    QMessageBox.warning(None, 'Warning','Для выполнения данной операции необходим {}-й уровень доступа'.format(r_level))
                    return
            return decorated2
        return decorator

    @login_required(3)
    def read_message(self):
        if self.ui.mode == 'Чтение':
            # client_lib.client_mes_read(sock)
            msg = self.chat_client.read_client_message()
            if msg:
                self.ui.chat_textBrowser.append(msg)

    @login_required(3)
    def write_message(self):
        msg = self.ui.send_mes.toPlainText()
        if msg == "":
            QMessageBox.warning(None, 'Warning', 'Нельзя отправить пустое сообщение. Введите текст')
            return True
        reply = QMessageBox.question(self, 'System_question', 'Отправить сообщение в общий чат?', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.No:
            to, ok = QtWidgets.QInputDialog.getText(self, 'System_question', 'Кому доставить сообщение? Введите логин: ')
            if ok:
                # msg_rcv = self.chat_client.get_client_key(to)
                # print(msg_rcv)
                self.chat_client.client_write_person(msg, to, self.ui.account_name, self.ui.session)
        else:
            self.chat_client.client_write_chat(msg, self.ui.account_name, self.ui.session)
        self.ui.chat_textBrowser.append("<font color='red' > My message: {}</font>".format(msg))
        self.ui.send_mes.clear()

