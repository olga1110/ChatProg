import sys
import os
import json
import time
import re
from functools import wraps
import hashlib

sys.path.append(os.path.dirname(__file__) + '/../')

import LIB.salt as salt
from LIB.errors import AccountNameError, ResponseCodeError
from DB.DB_classes import *
from log_config import create_server_log

logger = create_server_log('server_log.log')


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


class ServerHandler:

    def __init__(self, session, engine):
        self.session = session
        self.engine = engine

    def login_required(func):

        def wrap(self, *args):
            login = args[0]
            session_kod = args[1]
            sessions = args[2]
            if sessions.get(login) == session_kod:
                res = func(self, *args)
                return res
            raise Exception("User %s not login" % login)

        return wrap

    def log(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            result = func(*args, **kwargs)
            msg = 'вызов функции {} с аргументами: {}, {} выполнен'.format(func.__name__, args, kwargs)
            logger.debug(func.__doc__ + '\n' + msg)
            return result

        return wrap

    @staticmethod
    def message_encode(ex_data):
        """Кодировка cообщения для отправки на сокет"""
        return (json.dumps(ex_data)).encode('utf-8')

    @staticmethod
    def message_decode(im_data):
        """Расшифровка полученного сообщения"""
        return json.loads(im_data.decode('utf-8'))

    @staticmethod
    @log
    def send_response_to_client(sock, result):
        """Отправка ответа клиенту"""
        result_buf = ServerHandler.message_encode(result)
        sock.send(result_buf)

    @staticmethod
    @log
    def check_account_name(account_name):
        """Проверка логина"""
        if len(account_name) > 25:
            raise AccountNameError(account_name)
            logger.error('The lenth of the account name is more than 25 characters')
        elif len(account_name) < 4:
            logger.warning('Login consists of less than 4 characters, {}'.format(account_name))
        else:
            return 'ok'

    @staticmethod
    @log
    def check_server_response(result):
        """ Проверка ответа сервера (action = 'presense')"""
        if len(result) != 3:
            raise ResponseCodeError(result)
            logger.error('The lenth of the response code is not equal to 3')

    # @log
    # def sys_info(result, response_code):
    #     if response_code == 202:
    #         logger.info('Пользователь {} подключился к сети в {} со статусом {}'.format(result['user']['account_name'], result['time'], result['user']['status']))
    #     # else:
    #         logger.info('Пользователю отказано в доступе')

    @staticmethod
    @log
    def generate(password):
        """Генерация хэша пароля"""
        msg = hashlib.sha256()
        msg.update(password.encode())
        msg.update(salt.salt.encode())
        return msg.hexdigest()

    @log
    def create_registr_response(self, data):
        """Обработка запроса на регистрацию нового клиента в системе"""
        # pattern_password = '([\d+\w\])([!@#$%^&*]){8,}'
        pattern_password = re.compile(r'([\d+\w\])([!@#$%^&*]){8,}')
        if re.search(pattern_password, data['password']) is None:
            result = {'response': 402,
                      'info': 'Задан неверный пароль! Пароль должен содержать не менее 8 символов, включая строчные '
                              'или заглавные '
                              'латинские буквы, цифры и пунктационные знаки'}
        elif self.session.query(CUsers).filter_by(login=data['account_name'], level=int(data['level'])).all():
            result = {'response': 409, 'info': 'Пользователь с данным логином/уровнем доступа существует!'}
        elif data['password'] != data['password1']:
            result = {'response': 402, 'info': 'Пароли не совпадают!'}
        elif data['account_name'] == '' or data['password'] == '' or data['password1'] == '' or data['level'] == '':
            result = {'response': 400, 'info': 'Не заполнено(-ы) обязательное поле(-я).\n'
                                               ' Все поля, отмеченные *, являются обязательными для заполнения!'}
        elif data['account_name']:
            if self.check_account_name(data['account_name']) == 'ok':
                result = {'response': 200, 'info': 'Регистрация выполнена успешно!'}
            else:
                result = {'response': 402, 'info': 'Логин не может содержать более 25 символов!'}
        # result_buf = self.message_encode(result)
        # sock.send(result_buf)
        return result

    @log
    def create_presense_response(self, data):
        """Обработка запроса на аутентфикацию клиента в системе"""

        result = JIMResponse(data, self.session, self.engine).server_response
        return result


class ServerDB:
    def __init__(self, session, engine):
        self.session = session
        self.engine = engine

    @ServerHandler.log
    def insert_op_client(self, login, host, time):
        """Вставка записи в табл. op_client (подключение клиента)"""
        result = self.engine.execute("select guid from users where login = ?", login)
        guid = result.fetchall()[0][0]
        self.session.add(COpClient(user_id=guid, ip_adress=host, log_time=time))
        self.session.commit()

    @ServerHandler.login_required
    @ServerHandler.log
    def insert_messages(self, login, session_kod, user_sessions, data):
        """Вставка записи в табл. messages (общий чат)"""
        result = self.engine.execute("select guid from users where login = ?", (data['from']))
        guid_from = result.fetchall()[0][0]
        result = self.engine.execute("select guid from users where login = ?", (data['to']))
        guid_to = result.fetchall()[0][0]
        self.session.add(
            CMessages(user_from=guid_from, user_to=guid_to, send_time=data['time'], message=data['message']))
        self.session.commit()

        # Проверка и обновление списка контактов пользователей
        users_id = []
        result = self.engine.execute("select user_id from contacts_list where owner_id = ?", guid_from)
        # print(result.fetchall())
        for line in result.fetchall():
            users_id.append(line[0])
        if guid_to not in users_id:
            self.session.add(CContactsList(owner_id=guid_from, user_id=guid_to))
            self.session.commit()
            self.session.add(CContactsList(owner_id=guid_to, user_id=guid_from))
            self.session.commit()

    # {'action': 'msg', 'time': 1531313146.1733363, 'type': 'chat', 'to': '#chat', 'from': 'user_7', 'message': 'Hello'}

    @ServerHandler.login_required
    @ServerHandler.log
    def insert_chat_messages(self, login, session_kod, user_sessions, data):
        """Вставка записи в табл. chat_messages (личные сообщения)"""
        result = self.engine.execute("select guid from users where login = ?", (data['from']))
        guid_from = result.fetchall()[0][0]
        self.session.add(
            CChatMessages(user_from=guid_from, chat_name=data['to'], send_time=data['time'], message=data['message']))
        self.session.commit()

    @ServerHandler.log
    def insert_new_user(self, data):
        """Вставка записи в табл. users (добавление нового пользователя)"""
        h = ServerHandler.generate(data['password'])
        self.session.add(CPassword(h=h))
        self.session.commit()
        # pid = cursor.lastrowid
        result = self.engine.execute('select max(guid) from password')
        pid = result.fetchall()[0][0]
        self.session.add(CUsers(login=data['account_name'], level=int(data['level']), password=pid))
        self.session.commit()


class JIMResponse:

    def __init__(self, data, session, engine):
        self.data = data
        self.session = session
        self.engine = engine
        self._server_response = {'response': 202, 'alert': 'Login is accepted'}

    @property
    def server_response(self):
        """ Формирование ответа сервера (action='presense')"""
        if not ('action' in self.data) or not ('time' in self.data) or not ('user' in self.data) \
                or not ('account_name' in self.data['user']) or not (self.data['action'] == 'presense'):
            # logger.error('Client message is incorrect. Access is denied')
            self._server_response = {'response': 400, 'error': 'Wrong request/JSON-object'}
        else:
            h = ServerHandler.generate(self.data['user']['password'])
            # pid = cursor.lastrowid
            result = self.session.query(CUsers).filter_by(login=self.data['user']['account_name']).all()
            result1 = self.session.query(CUsers).filter_by(login=self.data['user']['account_name'],
                                                           level=self.data['user']['level']).all()
            result2 = self.engine.execute('select p.h  from users u, password p where u.password = p.guid' \
                                          ' and u.login = ? and u.level = ?',
                                          (self.data['user']['account_name'], self.data['user']['level']))
            if len(result) == 0:
                self._server_response = {'response': 402, 'error': 'Login is not registered!'}
            elif len(result1) == 0:
                self._server_response = {'response': 402,
                                         'error': '{}th level of access for login {} is not registered!'.format(
                                             self.data['user']['level'], self.data['user']['account_name'])}

            elif result2.fetchall()[0][0] != h:
                self._server_response = {'response': 402,
                                         'error': 'Wrong password for login {} and {}th level of access'.format(
                                             self.data['user']['account_name'], self.data['user']['level'])}

        return self._server_response


class ListContacts(JIMResponse):

    @ServerHandler.login_required
    @ServerHandler.log
    def get_client_contacts(self, login, session_kod, user_sessions, sock):
        """Обработка запроса на вывод списка контактов клиента"""

        result = self.engine.execute(
            "select count(user_id) from contacts_list where owner_id = (select guid from users where login = ?)", login)
        count = result.fetchall()[0][0]

        if self.data:
            self._server_response = {"response": 202, "quantity": count}
        else:
            self._server_response = {"response": 400, 'alert': 'Request is incorrect'}
        print('Ответ по запросу пользователя на получение списка контактов: {}'.format(self._server_response))
        ServerHandler.send_response_to_client(sock, self._server_response)
        if self._server_response['response'] == 202:
            contact_response = {"action": "contact_list"}
            result = self.engine.execute(
                "select login from contacts_list as cl inner join users as u on cl.user_id = u.guid where owner_id ="
                " (select guid from users where login = ?)",
                (login,))
            for line in result.fetchall():
                contact_response['user_id'] = line[0]
                ServerHandler.send_response_to_client(sock, contact_response)
                time.sleep(0.2)
        return self._server_response

    @ServerHandler.login_required
    @ServerHandler.log
    def modify_contact(self, login, session_kod, user_sessions, action, nickname):
        """Обработка запроса на модификацию списка контактов клиента"""
        result = self.engine.execute("select guid from users where login = ?", login)
        owner = result.fetchall()[0][0]
        result = self.engine.execute("select guid from users where login = ?", nickname)
        user_id = result.fetchall()[0][0]
        users_id = []
        result = self.engine.execute("select user_id from contacts_list where owner_id = ?", owner)
        # print(result.fetchall())
        for line in result.fetchall():
            users_id.append(line[0])
        if action == 'add_contact':
            if user_id not in users_id:
                self.session.add(CContactsList(owner_id=owner, user_id=user_id))
                self.session.commit()
                resp_add_cl = {'response': 202, 'error': None}
            else:
                resp_add_cl = {'response': 400, 'error': 'Пользователь {} уже есть в ваших контактах!'.format(nickname)}
            # resp_add_cl_snd = ServerHandler.message_encode(resp_add_cl)
            # sock.send(resp_add_cl_snd)
        if action == 'del_contact':
            if user_id in users_id:
                self.engine.execute("delete from contacts_list where owner_id = ? and user_id = ?", (owner, user_id))
                resp_add_cl = {'response': 202, 'error': None}
            else:
                resp_add_cl = {'response': 400, 'error': 'Пользователя {} нет в ваших контактах!'.format(nickname)}
            # resp_add_cl_snd = ServerHandler.message_encode(resp_add_cl)
            # sock.send(resp_add_cl_snd)
        return resp_add_cl

    @ServerHandler.log
    def create_chat(self, login, session_kod, user_sessions, data):
        """Создание пользовательского чата. Вставка записи в табл. users_chat"""
        self.session.add(CGroups(group_name=data['chat_name']))
        self.session.commit()
        # Добавляем пользователей в чат
        # Проверка что есть в users и вставка
        users_add = []
        users_error = []
        data['users'].append(login)
        result = self.engine.execute("select login from users")
        users_db = []
        for line in result.fetchall():
            users_db.append(line[0])
        for i in data['users']:
            if i in users_db:
                result = self.engine.execute("select guid from users where login = ?", i)
                user_id = result.fetchall()[0][0]
                result = self.engine.execute("select guid from groups where group_name = ?", (data['chat_name']))
                group_id = result.fetchall()[0][0]
                users_add.append(i)
                self.session.add(CUsersChat(group_id=group_id, user_id=user_id))
                self.session.commit()
            else:
                users_error.append(i)

        response_ok = 'Чат {} создан. Пользователи {} добавлены'.format(data['chat_name'], users_add)
        response_error = ''
        if users_error:
            response_error = 'Пользователя(ей) не существует: {}'.format(users_error)
        response = {'result': response_ok, 'error': response_error}
        # sock.send(ServerHandler.message_encode(response))
        return response
