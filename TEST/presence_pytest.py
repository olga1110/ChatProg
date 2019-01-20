import os
import sys
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(__file__) + '/../')

import LIB.server_lib as SL
import DB.DB_classes as DB

path = os.path.dirname(DB.__file__)
path_db = os.path.join(path, 'messages.db')

engine = create_engine('sqlite:///' + path_db)
session = sessionmaker(bind=engine)()


def setup_module(module):
    print('Запуск тестирования сервисной библиотеки')
    password = 'Jan2019!'
    login = 'Karina'

    h = SL.ServerHandler.generate(password)
    session.add(DB.CPassword(h=h))
    session.commit()
    result = engine.execute('select max(guid) from password')
    pid = result.fetchall()[0][0]
    session.add(DB.CUsers(login=login, level=1, password=pid))
    session.commit()
    print('Создана тестовая запись в БД с логином {}'.format(login))


def teardown_module():
    login = 'Karina'
    result = engine.execute('select p.guid from (select* from users where login = ?) as u inner join password as p on '
                            'u.password = p.guid', (login,))
    pid = result.fetchall()[0][0]
    engine.execute('delete from users where login = ?', (login,))
    engine.execute('delete from password where guid = ?', (pid,))
    session.commit()

    print('\nУдалена тестовая запись в БД с логином {}'.format(login))
    print('Завершение тестирования сервисной библиотеки')


@pytest.fixture(scope="module", params=[
    ({'time': 1534259654.223723, 'type': 'status',
      'user': {'account_name': 'Karina', 'status': 'online', 'level': '2', 'password': 'Jan2019!'}},
     {'response': 400, 'error': 'Wrong request/JSON-object'}),
    ({'action': 'presence', 'time': 1534259654.223723, 'type': 'status',
      'user': {'account_name': 'Karina', 'status': 'online', 'level': '1', 'password': 'Jan2019!'}},
     {'response': 202, 'alert': 'Login is accepted'}),
    ({'action': 'presence', 'time': 1534259654.223723, 'type': 'status',
      'user': {'account_name': '123', 'status': 'online', 'level': '2', 'password': 'Jan2019!'}},
     {'response': 402, 'error': 'Login is not registered!'}),
    ({'action': 'presence', 'time': 1534259654.223723, 'type': 'status',
      'user': {'account_name': 'Karina', 'status': 'online', 'level': '2', 'password': 'Jan2019!'}},
     {'response': 402, 'error': '2th level of access for login Karina is not registered!'}),
    ({'action': 'presence', 'time': 1534259654.223723, 'type': 'status',
      'user': {'account_name': 'Karina', 'status': 'online', 'level': '1', 'password': 'Jan2018!'}},
     {'response': 402, 'error': 'Wrong password for login Karina and 1th level of access'})
])
def param_test(request):
    return request.param


def test_get_server_response(param_test):
    data, expected_output = param_test
    result = SL.JIMResponse(data, session, engine).server_response
    print("\ninput: {0}, output: {1}, expected: {2}".format(data, result,
                                                            expected_output))
    assert result == expected_output
