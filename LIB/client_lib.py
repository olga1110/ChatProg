# Реализовать декоратор @log, фиксирующий обращение к декорируемой функции: сохраняет имя функции и её аргументы.

import sys
import json
import time
# import logging
# from log_config import log_client_init
from functools import wraps
sys.path.append("..")
from log_config import create_client_log


logger = create_client_log('client_log.log')
# log_client = logging.getLogger("client_messanger_log")
# log_client = None


def log_console(func):
    # global log_client
    # if log_client is None:
    # log_client = log_client_init()
    @wraps(func)
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug(func.__doc__)
        if __debug__:
            print('вызов функции {} с аргументами: {}, {} выполнен'.format(func.__name__, args, kwargs))
        return result

    return wrap

@log_console
def message_encode(ex_data):
    """Кодирование выполнено. Сообщение готово к отправке"""
    return (json.dumps(ex_data)).encode('utf-8')

@log_console
def message_decode(im_data):
    """Расшифровка сообщения выполнена"""
    return json.loads(im_data.decode('utf-8'))



class ClientHandler:

    def log_console(func):
        # global log_client
        # if log_client is None:
        # log_client = log_client_init()
        @wraps(func)
        def wrap(*args, **kwargs):
            result = func(*args, **kwargs)
            # log_client.debug(func.__doc__)
            if __debug__:
                print('вызов функции {} с аргументами: {}, {} выполнен'. format(func.__name__, args, kwargs))
            return result
        return wrap

    @staticmethod
    @log_console
    def start_for_client(sock, data):
        """Отправка и получение presense/registr сообщений"""
        data_buf = message_encode(data)
        sock.send(data_buf)
        result_buf = sock.recv(1024)
        result = message_decode(result_buf)
        if not isinstance(result, dict):
            # log_client.error('От сервера получен неверный формат ответа')
            raise TypeError
        return result

    @staticmethod
    @log_console
    def client_mes_read(sock):
        """Получено клиентское сообщение"""
        msg_from_server = sock.recv(1024)
        input_message = message_decode(msg_from_server)
        return "{}: {}".format(input_message['from'], input_message['message'])

    @staticmethod
    @log_console
    def read_server_response_contacts(sock):
        """Получен ответ от сервера с общим кол-ом контактов"""
        msg_from_server = sock.recv(4096)
        input_message = message_decode(msg_from_server)
        if 'action' not in input_message:
            count = input_message['quantity']
            return count
        return input_message

    @staticmethod
    @log_console
    def client_write_chat(sock, msg, account_name, session):
        """Отправлено клиентское сообщение"""
        msg_chart = ChatMessage(account_name, 'msg', 'chat', msg, session).get_client_message()
        msg_to_server = message_encode(msg_chart)
        sock.send(msg_to_server)
        print(msg_chart)
        return msg_chart

    @staticmethod
    @log_console
    def client_write_person(sock, msg, to, account_name, session):
        """Отправлено private - сообщение клиенту"""
        personal_msg = PrivateMessage(account_name, 'msg', 'personal', to, msg, session).get_client_message()
        msg_to_server = message_encode(personal_msg)
        sock.send(msg_to_server)
        return personal_msg

    @staticmethod
    @log_console
    def get_contacts(sock, session):
        request = {'action': 'get_contacts', 'session': session, 'time': time.time()}
        request_snd = message_encode(request)
        sock.send(request_snd)
        return request

    @staticmethod
    @log_console
    def get_request_modify(sock, action, nickname, session):
        request = {'action': action, 'user_id': nickname, 'session': session, 'time': time.time()}
        print(request)
        request_snd = message_encode(request)
        sock.send(request_snd)
        return request

    @staticmethod
    @log_console
    def create_chat(sock, chat_name, users_id, session):
        request = {'action': 'create_chat', 'chat_name': chat_name, 'session': session, 'users': users_id}
        request_snd = message_encode(request)
        sock.send(request_snd)
        return request


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

    @log_console
    def get_client_message(self):
        """Создано сообщение presense для отправки на сервер"""
        return self._client_message


class PresenseMessage(JIMMessage):

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


# {'action': 'msg', 'time': 1531313146.1733363, 'type': 'chat', 'to': '#chat', 'from': 'user_7', 'message': 'Hello'}

















