import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QLabel, QComboBox
from PyQt5.QtCore import *
# from PyQt5.QtGui import *
from GUI.chat_ui import Ui_Form as ui_chat
from LIB.client import Client, Chat, ListContacts


class ReadThread(QThread):
    in_msg = pyqtSignal(str)

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.chat_client = Chat(sock)
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            msg = self.chat_client.read_client_message()
            if msg:
                self.in_msg.emit(msg)


class WriteThread(QThread):
    out_msg = pyqtSignal(str)

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


# class ComboBox(QtWidgets.QComboBox):
#     popupAboutToBeShown = QtCore.pyqtSignal()
#
#     def showPopup(self):
#         self.popupAboutToBeShown.emit()
#         super(ComboBox, self).showPopup()


class CChatForm(QtWidgets.QWidget):
    incomeMessage = QtCore.pyqtSignal(str)

    def __init__(self, sock, account_name, level, session, contacts, parent=None):
        super().__init__(parent)
        self.ui = ui_chat()
        self.sock = sock
        self.ui.level = level
        self.ui.session = session
        self.contacts = contacts
        # timer = QtCore.QTimer(self)
        # timer.start(3000)
        # timer.timeout.connect(self.read_message)
        self.ui.setupUi(self)
        self.ui.user_textBrowser.setText(account_name)
        self.ui.account_name = account_name

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("GUI/Img/send.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.send_button.setIcon(icon)
        self.ui.send_button.setIconSize(QtCore.QSize(70, 70))

        self.ui.send_button.clicked.connect(self.write_message)
        button_style = 'QPushButton {background-color: #98B9DB; border: 1px solid #E32828; border-radius: 20px;}'
        self.ui.exit_button.setStyleSheet(button_style)
        self.ui.exit_button.clicked.connect(self.close)
        self.ui.Private_RB.setChecked(True)
        self.ui.Chat_RB.toggled.connect(self.hide_contacts)
        self.to_contact = '<Пусто>'
        self.ui.list_contacts_combo.addItem('Выберите контакт')
        self.ui.list_contacts_combo.addItems(self.contacts)
        self.ui.list_contacts_combo.adjustSize()
        # self.list_contacts_combo.popupAboutToBeShown.connect(self.populateConbo)
        self.ui.list_contacts_combo.activated[str].connect(self.onActivated)

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
                    QMessageBox.warning(None, 'Warning', 'Для выполнения данной операции необходим {}-й уровень доступа'
                                        .format(r_level))
                    return
            return decorated2
        return decorator

    def hide_contacts(self):
        if self.ui.Chat_RB.isChecked():
            self.ui.list_contacts_combo.hide()
        else:
            self.ui.list_contacts_combo.show()

    @login_required(3)
    def write_message(self, sock):
        msg = self.ui.send_mes.toPlainText()
        if msg == "":
            QMessageBox.warning(None, 'Warning', 'Нельзя отправить пустое сообщение. Введите текст')
            return True

        if self.ui.Chat_RB.isChecked():
            type_msg = 'chat'
            to = 'chat'
        else:
            type_msg = 'personal'
            to = self.to_contact
            if self.to_contact in ('Выберите контакт', '<Пусто>'):
                QMessageBox.warning(None, 'Warning', 'Получатель не выбран!')
                return True


        self.thread1 = WriteThread(self.sock, msg, type_msg, to, self.ui.account_name, self.ui.session)

        self.thread1.out_msg.connect(self.on_WriteThreadSignal)
        self.thread1.start()

    def on_WriteThreadSignal(self, value):
        self.ui.chat_textBrowser.append("<font color='red' > My message: {}</font>".format(value))
        self.ui.send_mes.clear()

    def on_ReadThreadSignal(self, value):
        self.ui.chat_textBrowser.append(value)

    def onActivated(self, text):
        self.to_contact = text
        return self.to_contact

    # def populateConbo(self):
    #     if self.list_contacts_combo.count() == 1:
    #         list_contacts = self.get_contacts()
    #         self.list_contacts_combo.addItems(list_contacts)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     'Выйти из ChatFree?', QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
