import unittest
from unittest.mock import Mock
import os
import sys
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(__file__) + '/../')

from LIB.server_lib import ServerHandler
import DB.DB_classes as DB


path = os.path.dirname(DB.__file__)
path_db = os.path.join(path, 'messages.db')
engine = create_engine('sqlite:///' + path_db)
session = sessionmaker(bind=engine)()


class CTestLib(unittest.TestCase):
    def test_presense_response(self):
        data = {
            'action': 'presense',
            'time': time.time(),
            'type': 'status',
            'user': {
                'account_name': 'User10',
                'password': 'Jan2019!',
                'status': 'online',
                'level': 1,
            }
        }
        virt_sock = Mock()
        virt_sock.send.return_value = None
        virt_sock.recv.return_value = data
        result = ServerHandler(session, engine).create_presense_response(data)
        self.assertDictEqual(result, {'response': 202, 'alert': 'Login is accepted'})


if __name__ == '__main__':
    unittest.main()



