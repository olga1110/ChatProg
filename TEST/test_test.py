
import os
import sys
# import pytest

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


def test_testing():
    data = {'time': 1534259654.223723, 'type': 'status', 'user': {'account_name': 'Alex', 'status': 'online', 'level': '2', 'password': '12345678'}}
    result = SL.JIMResponse(data, session, engine).get_server_response()
    assert result == {'response': 400, 'error': 'Wrong request/JSON-object'}
# expected_output = {'response': 400, 'error': 'Wrong request/JSON-object'}

# if not ('action' in data):
#     print('gggggg')
#
#
#
# if not ('action' in data) or not ('time' in data) or not ('user' in data) \
#                 or not ('account_name' in data['user']) or not (data['action'] == 'presense'):
#     print('gggggg')








# result = SL.JIMResponse(data, session, engine).get_server_response()
# print(result)






