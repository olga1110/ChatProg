#функции на серверной части

# Реализовать декоратор @log, фиксирующий обращение к декорируемой функции: сохраняет имя функции и её аргументы.


import sys
import os
import json
import time
# from log_config import log_serv_init
# import logging
from functools import wraps
import hashlib
from errors import AccountNameError, ResponseCodeError
import sqlite3
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import salt as salt
# os.chdir('..')
sys.path.append(os.path.join(os.getcwd(), 'DB'))
from DB_classes import *
# logger = log_serv_init()
# logger = logging.getLogger("server_messanger_log")

# Подключение к базе данных
path_db = os.path.join(os.getcwd(), 'DB', 'messages.db')
path_db1 = 'sqlite:///' + path_db
engine = create_engine(path_db1)
session = sessionmaker(bind=engine)()
conn = sqlite3.connect(path_db, check_same_thread=False)
cursor = conn.cursor()


def log(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        # logger.debug(func.__doc__)
        if __debug__:
            print('вызов функции {} с аргументами: {}, {} выполнен'. format(func.__name__, args, kwargs))
        return result
    return wrap



@log
def message_encode(ex_data):
    """ Кодирование выполнено. Сообщение готово к отправке"""
    return (json.dumps(ex_data)).encode('utf-8')


@log
def message_decode(im_data):
    """ Расшифровка сообщения выполнена"""
    return json.loads(im_data.decode('utf-8'))

@log
def check_account_name(account_name):
    """ Проверка логина выполнена"""
    if len(account_name) > 25:
        raise AccountNameError(account_name)
        # logger.error('The lenth of the account name is more than 25')
    # elif len(account_name) < 4:
        # logger.warning('Логин состоит из менее, чем 4 символов, {}'.format(account_name))
    else:
        return 'ok'


# @log
# def check_server_response(result):
#     """ Проверка ответа сервера выполнена"""
#     if len(result) != 3:
#         raise ResponseCodeError(result)
#         logger.error('The lenth of the response code is not equal to 3')


# @log
# def sys_info(result, response_code):
#     if response_code == 202:
#         logger.info('Пользователь {} подключился к сети в {} со статусом {}'.format(result['user']['account_name'], result['time'], result['user']['status']))
#     # else:
#         logger.info('Пользователю отказано в доступе')

@log
def generate(password):

    msg = hashlib.sha256()
    msg.update(password.encode())
    msg.update(salt.salt.encode())
    return msg.hexdigest()


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

class JIMResponse:

    def __init__(self, data):
        self.data = data
        # self._response = {}

    def get_server_response(self):
        """ Проверка presense сообщения клиента выполнена"""
        if not ('action' in self.data) or not ('time' in self.data) or not ('user' in self.data) \
                or not ('account_name' in self.data['user']) or not (self.data['action'] == 'presense'):
            # logger.error('Client message is incorrect. Access is denied')
            self._server_response = {'response': 400, 'error': 'Wrong request/JSON-object'}

        else:
            self._server_response = {'response': 202, 'alert': 'Login is accepted'}
        return self._server_response


class ListContacts(JIMResponse):

    def login_required(func):

        def wrap(self, *args):
            login = args[1]
            session_kod = args[2]
            sessions = args[3]
            if sessions.get(login) == session_kod:
                res = func(self, *args)
                return res

            raise Exception("User %s not login" % login)

        return wrap

    @login_required
    def get_client_contacts(self, sock, login, session_kod, user_sessions):

        result = engine.execute(
            "select count(user_id) from contacts_list where owner_id = (select guid from users where login = ?)", (login))
        count = result.fetchall()[0][0]

        if self.data:
            self._server_response = {"response": 202, "quantity": count}
        else:
            self._server_response = {"response": 400, 'alert': 'Request is incorrect'}
        print('Ответ по запросу пользователя на получение списка контактов: {}'.format(self._server_response))
        sock.send(message_encode(self._server_response))
        if self._server_response['response'] == 202:
            contact_response = {"action": "contact_list"}
            result = engine.execute(
                "select login from contacts_list as cl inner join users as u on cl.user_id = u.guid where owner_id = (select guid from users where login = ?)",
                (login))
            for line in result.fetchall():
                contact_response['user_id'] = line[0]
                print(contact_response)
                contact_response_snd = message_encode(contact_response)
                sock.send(contact_response_snd)
                time.sleep(0.2)
        return self._server_response

    # def send_client_contacts(self, sock, login):
    #     contact_response = {"action": "contact_list"}
    #     result = engine.execute(
    #         "select login from contacts_list as cl inner join users as u on cl.user_id = u.guid where owner_id = (select guid from users where login = ?)", (login))
    #     for line in result.fetchall():
    #         contact_response['user_id'] = line[0]
    #         print(contact_response)
    #         contact_response_snd = message_encode(contact_response)
    #         sock.send(contact_response_snd)
    #         time.sleep(0.2)
#-----------------------------------------------------------------------------------------
    @login_required
    def modify_contact(self, sock, login, session_kod, user_sessions, action, nickname):
        result = engine.execute("select guid from users where login = ?", login)
        owner = result.fetchall()[0][0]
        result = engine.execute("select guid from users where login = ?", (nickname))
        user_id = result.fetchall()[0][0]

        users_id = []
        result = engine.execute("select user_id from contacts_list where owner_id = ?", (owner))
        # print(result.fetchall())
        for line in result.fetchall():
            users_id.append(line[0])
        if action == 'add_contact':
            if user_id not in users_id:
                session.add(CContactsList(owner_id=owner, user_id=user_id))
                session.commit()
                resp_add_cl = {'response': 202, 'error': None}
            else:
                resp_add_cl = {'response': 400, 'error': 'Пользователь {} уже есть в ваших контактах!'.format(nickname)}
            resp_add_cl_snd = message_encode(resp_add_cl)
            sock.send(resp_add_cl_snd)
        if action == 'del_contact':
            if user_id in users_id:
                engine.execute("delete from contacts_list where owner_id = ? and user_id = ?", (owner, user_id))
                resp_add_cl = {'response': 202, 'error': None}
            else:
                resp_add_cl = {'response': 400, 'error': 'Пользователя {} нет в ваших контактах!'.format(nickname)}
            resp_add_cl_snd = message_encode(resp_add_cl)
            sock.send(resp_add_cl_snd)
        return resp_add_cl_snd


class ServerHandler:

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

    def create_registr_response(self, sock, data):
        if session.query(CUsers).filter_by(login=data['account_name'], level=int(data['level'])).all():
            result = {'response': 409, 'info': 'Пользователь с данным логином/уровнем доступа существует!'}
        elif data['password'] != data['password1']:
            result = {'response': 402, 'info': 'Пароли не совпадают!'}
        elif data['account_name'] == '' or data['password'] == '' or data['password1'] == '' or data['level'] == '':
            result = {'response': 400, 'info': 'Не заполнено(-ы) обязательное поле(-я).\n'
                                              ' Все поля являются обязательными для заполнения'}
        elif data['account_name']:
            if check_account_name(data['account_name']) == 'ok':
                result = {'response': 200, 'info': 'Регистрация выполнена успешно!'}
            else:
                result = {'response': 402, 'info': 'Логин не может содержать более 25 символов!'}

        result_buf = message_encode(result)
        sock.send(result_buf)
        return result

    def create_presense_response (self, sock, data):
        # if 'account_name' in data['user']:
        #     check_account_name(data['user']['account_name'])

        result = JIMResponse(data).get_server_response()
        # check_server_response(result['response'])
        # sys_info(data, result['response'])
        result_buf = message_encode(result)
        sock.send(result_buf)
        return result


    def insert_op_client(self, login, host, time):
        result = engine.execute("select guid from users where login = ?", (login))
        guid = result.fetchall()[0][0]
        session.add(COpClient(user_id=guid, ip_adress=host, log_time=time))
        session.commit()

    @login_required
    def insert_messages(self, login, session_kod, user_sessions, data):
        result = engine.execute("select guid from users where login = ?", (data['from']))
        guid_from = result.fetchall()[0][0]
        result = engine.execute("select guid from users where login = ?", (data['to']))
        guid_to = result.fetchall()[0][0]
        session.add(CMessages(user_from=guid_from, user_to = guid_to, send_time=data['time'], message=data['message']))
        session.commit()

        # Проверка и обновление списка контактов пользователей
        users_id = []
        result = engine.execute("select user_id from contacts_list where owner_id = ?", (guid_from))
        # print(result.fetchall())
        for line in result.fetchall():
            users_id.append(line[0])
        if guid_to not in users_id:
            session.add(CContactsList(owner_id=guid_from, user_id=guid_to))
            session.commit()
            session.add(CContactsList(owner_id=guid_to, user_id=guid_from))
            session.commit()

    # {'action': 'msg', 'time': 1531313146.1733363, 'type': 'chat', 'to': '#chat', 'from': 'user_7', 'message': 'Hello'}

    @login_required
    def insert_chat_messages(self, login, session_kod, user_sessions, data):
        result = engine.execute("select guid from users where login = ?", (data['from']))
        guid_from = result.fetchall()[0][0]
        session.add(CChatMessages(user_from=guid_from, chat_name=data['to'], send_time=data['time'], message=data['message']))
        session.commit()

    def insert_new_user(self, data):
        h = generate(data['password'])
        print(h)
        session.add(CPassword(h = h))
        session.commit()
        # pid = cursor.lastrowid
        result = engine.execute('select max(guid) from password')
        pid = result.fetchall()[0][0]
        session.add(CUsers(login=data['account_name'], level=int(data['level']), password=pid))
        session.commit()

    def create_chat(self, sock, login, session_kod, user_sessions, data):
        # Создаем чат
        session.add(CGroups(group_name=data['chat_name']))
        session.commit()
        # Добавляем пользователей в чат
        # Проверка что есть в users и вставка
        users_add = []
        users_error = []
        data['users'].append(login)
        result = engine.execute("select login from users")
        users_db = []
        for line in result.fetchall():
            users_db.append(line[0])
        for i in data['users']:
            if i in users_db:
                result = engine.execute("select guid from users where login = ?", (i))
                user_id = result.fetchall()[0][0]
                result = engine.execute("select guid from groups where group_name = ?", (data['chat_name']))
                group_id = result.fetchall()[0][0]
                users_add.append(i)
                session.add(CUsersChat(group_id=group_id, user_id=user_id))
                session.commit()
            else:
                users_error.append(i)

        response_ok = 'Чат {} создан. Пользователи {} добавлены'.format(data['chat_name'], users_add)
        response_error = ''
        if users_error:
            response_error = 'Пользователя(ей) не существует: {}'.format(users_error)
        response = {'result': response_ok, 'error': response_error}
        sock.send(message_encode(response))
        return response


