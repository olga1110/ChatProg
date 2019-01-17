from socket import *
import sys
import time
import json
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from Crypto.PublicKey import RSA
import ssl
from functools import wraps
# import LIB.client_lib as client_lib
from DB.DB_classes import *
from log_config import create_client_log

logger = create_client_log('client_log.log')


# ---------Метообъекты-----------------------------------------------
class Singleton(type):

    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class CDesc:

    def __init__(self, name):
        self.__name = name

    def __set__(self, instance, value):
        if len(value) > 25:
            print('Логин должен быть не более 25 символов')
        elif len(value) < 4:
            print('Логин должен быть не менее 4 символов')
        instance.__dict__[self.__name] = value

    def __get__(self, instance, cls):

        if self.__name in instance.__dict__:
            return instance.__dict__[self.__name]
        return 0


class CCls:
    account_name = CDesc('account_name')


# ---------Метообъекты-----------------------------------------------

# Общие методы-----------------------------------------------
class ClientHandler:

    def log(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            result = func(*args, **kwargs)
            msg = 'вызов функции {} с аргументами: {}, {} выполнен'.format(func.__name__, args, kwargs)
            logger.debug(func.__doc__ + '\n' + msg)
            # if __debug__:
            #     print('вызов функции {} с аргументами: {}, {} выполнен'. format(func.__name__, args, kwargs))
            return result

        return wrap

    @staticmethod
    def message_encode(ex_data):
        """Кодировка сообщения"""
        return (json.dumps(ex_data)).encode('utf-8')

    @staticmethod
    def message_decode(im_data):
        """Расшифровка сообщения"""
        return json.loads(im_data.decode('utf-8'))

    @classmethod
    def start_for_client(cls, sock, data):
        """Отправка и получение presence/registr сообщений"""
        # data_buf = (json.dumps(data)).encode('utf-8')
        data_buf = cls.message_encode(data)
        sock.send(data_buf)
        result_buf = sock.recv(1024)
        result = cls.message_decode(result_buf)
        if not isinstance(result, dict):
            logger.error('От сервера получен неверный формат ответа')
            raise TypeError
        return result


# ---------------------- Типы сообщений------------------------------

class JIMMessage:

    def __init__(self, account_name, action, type):
        self.account_name = account_name
        self.action = action
        self.type = type
        self._client_message = {
            'action': self.action,
            'time': time.time(),
            'type': self.type
        }

    @property
    def request_to_server(self):
        """Создание presence-сообщения для отправки на сервер"""
        return self._client_message


class presenceMessage(JIMMessage):

    def __init__(self, account_name, action, type, user_status, level, password):
        super().__init__(account_name, action, type)
        self.user_status = user_status
        self.level = level
        self.password = password

        if self.user_status == 'Y':
            self._status = 'online'
        else:
            self._status = 'offline'
        self._client_message['user'] = {}
        self._client_message['user']['account_name'] = self.account_name
        self._client_message['user']['status'] = self._status
        self._client_message['user']['level'] = self.level
        self._client_message['user']['password'] = self.password


class RegisterMessage(JIMMessage):

    def __init__(self, account_name, action, type, level, password, password1):
        super().__init__(account_name, action, type)
        self.account_name = account_name
        self.level = level
        self.password = password
        self.password1 = password1
        self._client_message['account_name'] = self.account_name
        self._client_message['level'] = self.level
        self._client_message['password'] = self.password
        self._client_message['password1'] = self.password1


class ChatMessage(JIMMessage):

    def __init__(self, account_name, action, type, msg, session):
        super().__init__(account_name, action, type)
        self.msg = msg
        self.session = session
        self._to = '#chat'
        self._from = account_name
        self._client_message['to'] = self._to
        self._client_message['from'] = self.account_name
        self._client_message['message'] = self.msg
        self._client_message['session'] = self.session


class PrivateMessage(JIMMessage):

    def __init__(self, account_name, action, type, to, msg, session):
        super().__init__(account_name, action, type)
        self.msg = msg
        self.to = to
        self.session = session
        self._from = account_name
        self._client_message['to'] = self.to
        self._client_message['from'] = self.account_name
        self._client_message['message'] = self.msg
        self._client_message['session'] = self.session


class Client(metaclass=Singleton):
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        # self.s = ssl.wrap_socket(self.s, ciphers="AES128-SHA")
        self.s.connect((addr, port))

    # presence-сообщение
    @ClientHandler.log
    def get_account_name(self, user_name):
        """Проверка логина"""
        #     user_name = input('Введите ваш логин: ')
        #     while user_name == '':
        #         user_name = input('Введите ваш логин: ')
        account_name = CCls().account_name
        account_name = user_name
        return account_name

    def get_user_status(self):
        """Проверка статуса"""
        # user_status = input('Ваш статус - online? (Y/N)')
        user_status = 'Y'
        return user_status

    @ClientHandler.log
    def get_register_response(self, account_name, level, password, password1):
        """Получение ответа сервера по регистрации в системе"""
        data = RegisterMessage(account_name, 'register', 'registration', level, password, password1).request_to_server
        server_response = ClientHandler.start_for_client(self.s, data)
        return server_response

    @ClientHandler.log
    def get_presence_response(self, account_name, user_status, level, password):
        """Получение ответа сервера по аутентификации в системе"""
        data = presenceMessage(account_name, 'presence', 'status', user_status, level, password).request_to_server
        server_response = ClientHandler.start_for_client(self.s, data)
        return server_response


class Chat:
    def __init__(self, sock):
        self.s = sock
        # self._handler = ClientHandler()

    @ClientHandler.log
    def read_client_message(self):
        """Чтение сообщения"""
        msg_from_server = self.s.recv(1024)
        input_message = ClientHandler.message_decode(msg_from_server)
        if input_message:
            return '{}: {}'.format(input_message['from'], input_message['message'])
        # return ''

    @ClientHandler.log
    def client_write_chat(self, msg, account_name, session):
        """Отправка сообщения в чат"""
        msg_chart = ChatMessage(account_name, 'msg', 'chat', msg, session).request_to_server
        msg_to_server = ClientHandler.message_encode(msg_chart)
        self.s.send(msg_to_server)
        return msg_chart

    @ClientHandler.log
    def client_write_person(self, msg, to, account_name, session):
        """Отправка личного сообщения"""
        personal_msg = PrivateMessage(account_name, 'msg', 'personal', to, msg, session).request_to_server
        msg_to_server = ClientHandler.message_encode(personal_msg)
        self.s.send(msg_to_server)
        return personal_msg

    # def get_client_key(self, to, msg):
    # def get_client_key(self, to):
    #     request_key = {'action': 'get_key', 'user_login': to}
    #     print(request_key)
    #     self.s.send(client_lib.message_encode(request_key))
    #     # # user_key = self.s.recv(1024)
    #     # # msg_bytes = client_lib.message_encode(msg)
    #     # pub_key = RSA.importKey((self.s.recv(1024).decode()), passphrase=None)
    #     # return rsa.encrypt(msg_bytes, pub_key)
    #     return RSA.importKey((self.s.recv(1024).decode()), passphrase=None)


class ListContacts:
    def __init__(self, sock):
        self.s = sock
        # self._handler = ClientHandler()

    @ClientHandler.log
    def client_get_contacts(self, session):
        """Отправка запроса на получение списка контактов"""
        request = {'action': 'get_contacts', 'session': session, 'time': time.time()}
        print(request)
        request_snd = ClientHandler.message_encode(request)
        self.s.send(request_snd)
        print(request)
        return request

    @ClientHandler.log
    def read_server_response_contacts(self):
        """Получение списка контактов от сервера"""
        server_response_rcv = self.s.recv(4096)
        server_response_contacts = ClientHandler.message_decode(server_response_rcv)
        if 'action' not in server_response_contacts:
            count = server_response_contacts['quantity']
            return count
        return server_response_contacts

    @ClientHandler.log
    def get_request_modify(self, action, nickname, session):
        """Отправка запроса на изменение списка контактов"""
        request = {'action': action, 'user_id': nickname, 'session': session, 'time': time.time()}
        request_snd = ClientHandler.message_encode(request)
        self.s.send(request_snd)
        return request

    @ClientHandler.log
    def create_chat(self, chat_name, users_id, session):
        """Отправка запроса на создание чата"""
        request = {'action': 'create_chat', 'chat_name': chat_name, 'session': session, 'users': users_id}
        request_snd = ClientHandler.message_encode(request)
        self.s.send(request_snd)
        return request


# Консольная версия. Сейчас не используется. Запуск GUI chat.py
if __name__ == '__main__':

    # Подключение клиента
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

    s = Client(addr, port)

    # account_name = s.get_account_name(user_name)
    # account_name = user_name

    user_status = s.get_user_status()

    # Подключение к базе данных
    engine = create_engine('sqlite:///clients_messages.db')
    session = sessionmaker(bind=engine)()

    # presence-сообщение и ответ сервера
    result = s.get_server_response()
    print('Ответ от сервера получен: {}'.format(result))

    # Общий чат
    chat_client = Chat(s.s)

    # Работа со списком контактов
    list_contacts = ListContacts(s.s)

    # Работа со списком контактов
    modify_request = 'Y'
    while modify_request == 'Y':
        contacts_list = input("Для получения списка контактов нажмите 'L'/ \n"
                              "Для добавления контакта нажмите 'A'/\n"
                              "Для удаления контакта нажмите 'D'/\n"
                              "Для создания чата нажмите 'C'/\n"
                              "Для перехода в основной режим нажмите любую клавишу: ")
        # Вывод списка контактов
        if contacts_list == 'L':
            list_contacts.client_get_contacts(session)
            count = list_contacts.read_server_response_contacts()
            print('Ваш список контактов:')
            for _ in range(count):
                list_contacts.read_server_response_contacts()
        # Запрос на добавление/удаление контактов
        elif contacts_list == 'A' or contacts_list == 'D':
            nickname = input("Введите логин для добавления/удаления пользователя: ")
            if contacts_list == 'A':
                action = 'add_contact'
            elif contacts_list == 'D':
                action = 'del_contact'
            list_contacts.get_request_modify(action, nickname, session)
            server_response_rcv = s.s.recv(4096)
            server_response = ClientHandler.message_decode(server_response_rcv)
            if server_response['response'] == '202':
                print('Операция выполнена успешно')
            else:
                print(server_response['error'])

        elif contacts_list == 'C':
            # Создание группы
            users_id = []
            chat_name = input("Задайте имя чата: ")
            while chat_name == '':
                chat_name = input("Задайте имя чата: ")
            add_user = 'Y'
            while add_user == 'Y':
                user_id = input('Для добавления в чат пользователя введите логин: ')
                users_id.append(user_id)
                add_user = input('Добавить нового пользователя,(Y/N)?')
            chat_client.create_chat(chat_name, users_id)
            server_response_rcv = s.s.recv(4096)
            server_response = ClientHandler.message_decode(server_response_rcv)
            print(server_response)
        modify_request = input("Продолжить работу со списком контактов,(Y/N)?")

    # Режим мессенджера
    if mode == 'r':
        while True:  # Постоянный опрос сервера
            # client_lib.client_mes_read(s)
            chat_client.read_client_message()

    if mode == 'w':
        while True:
            msg = input("Введите сообщение: ")
            chat = input('Сообщение для чата? (Y/N)')
            if chat != 'Y':
                chat = 'N'
            if chat == 'N':
                to = input("Кому доставить сообщение? Введите логин: ")
                chat_client.client_write_person(msg, to, account_name, session)
            else:
                chat_client.client_write_chat(msg, account_name, session)

    s.close()
