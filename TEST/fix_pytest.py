import os
import sys
import pytest

import sqlite3
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import LIB.server_lib as SL
import DB.DB_classes as db

os.chdir('..')
path_db = os.path.join(os.getcwd(), 'DB', 'messages.db')
path_db1 = 'sqlite:///' + path_db
engine = create_engine(path_db1)
session = sessionmaker(bind=engine)()
conn = sqlite3.connect(path_db, check_same_thread=False)
cursor = conn.cursor()


def setup_module(module):
    print('Запуск тестирования сервисной библиотеки')
    password = '12345678'
    login = 'Alex'

    h = SL.generate(password)
    session.add(db.CPassword(h=h))
    session.commit()
    result = engine.execute('select max(guid) from password')
    pid = result.fetchall()[0][0]
    session.add(db.CUsers(login=login, level=1, password=pid))
    session.commit()
    print('Создана тестовая запись в БД с логином {}'.format(login))


def teardown_module():
    login = 'Alex'
    result = cursor.execute(
        "select p.guid from (select* from users where login = ?) as u inner join password as p on u.password = p.guid",
        ([login]))
    pid = result.fetchall()[0][0]
    cursor.execute('delete from users where login = ?', [login])
    cursor.execute('delete from password where guid = ?', [pid])
    conn.commit()
    print('\nУдалена тестовая запись в БД с логином {}'.format(login))
    print('Завершение тестирования сервисной библиотеки')


@pytest.fixture(scope="module", params=[
({'time': 1534259654.223723, 'type': 'status', 'user': {'account_name': 'Alex', 'status': 'online', 'level': '2', 'password': '12345678'}}, {'response': 400, 'error': 'Wrong request/JSON-object'}),
({'action': 'presense', 'time': 1534259654.223723, 'type': 'status', 'user': {'account_name': 'Alex', 'status': 'online', 'level': '1', 'password': '12345678'}}, {'response': 202, 'alert': 'Login is accepted'}),
({'action': 'presense', 'time': 1534259654.223723, 'type': 'status', 'user': {'account_name': '123', 'status': 'online', 'level': '2', 'password': '12345678'}}, {'response': 402, 'error': 'Логин не зарегистрирован!'}),
({'action': 'presense', 'time': 1534259654.223723, 'type': 'status', 'user': {'account_name': 'Alex', 'status': 'online', 'level': '2', 'password': '12345678'}}, {'response': 402, 'error': 'уровень доступа 2 для логина Alex не зарегистрирован!'}),
({'action': 'presense', 'time': 1534259654.223723, 'type': 'status', 'user': {'account_name': 'Alex', 'status': 'online', 'level': '1', 'password': '1234567'}},{'response': 402, 'error': 'Неверный пароль для логина Alex и 1 уровня доступа'})
])
def param_test(request):
    return request.param


def test_get_server_response(param_test):
    data, expected_output = param_test
    result = SL.JIMResponse(data, session, engine).get_server_response()
    print("\ninput: {0}, output: {1}, expected: {2}".format(data, result,
                                                            expected_output))
    assert result == expected_output

#------------------------------------------------------------------------------------------------------------------------
# class JIMResponse:
#
#     def __init__(self, data):
#         self.data = data
#         # self._response = {}
#
#     def get_server_response(self):
#         """ Проверка presense сообщения клиента выполнена"""
#         if not ('action' in self.data) or not ('time' in self.data) or not ('user' in self.data) \
#                 or not ('account_name' in self.data['user']) or not (self.data['action'] == 'presense'):
#             # logger.error('Client message is incorrect. Access is denied')
#             self._server_response = {'response': 400, 'error': 'Wrong request/JSON-object'}
#         else:
#             h = hashlib.generate(self.data['user']['password'])
#             # pid = cursor.lastrowid
#             result = session.query(CUsers).filter_by(login=self.data['user']['account_name']).all()
#             result1 = session.query(CUsers).filter_by(login=self.data['user']['account_name'], level=self.data['user']['level']).all()
#             result2 = engine.execute('select p.h  from users u, password p where u.password = p.guid'\
#                                      ' and u.login = ? and u.level = ?', (self.data['user']['account_name'], self.data['user']['level']))
#             if len(result) == 0:
#                 self._server_response = {'response': 402, 'error': 'Логин не зарегистрирован!'}
#             elif len(result1) == 0:
#                 self._server_response = {'response': 402, 'error': 'уровень доступа {} для логина {} не зарегистрирован!'.format(self.data['user']['level'], self.data['user']['account_name'])}
#             elif result2.fetchall()[0][0] != h:
#                 self._server_response = {'response': 402, 'error': 'Неверный пароль для логина {} и {} уровня доступа'.format(self.data['user']['account_name'], self.data['user']['level'])}
#             else:
#                 self._server_response = {'response': 202, 'alert': 'Login is accepted'}
#             return self._server_response
# # ------------------------------------------------------------------------------------------------------------------------
#
# ({'action': 'presense', 'time': 1534259654.223723, 'type': 'status', 'user': {'account_name': 'Olga', 'status': 'online', 'level': '2', 'password': '777'}},)
