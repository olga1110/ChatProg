import unittest
import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../')

import LIB.server_lib as server_lib
from LIB.errors import AccountNameError, ResponseCodeError


class TestLib(unittest.TestCase):

    def test_message_encode(self):
        my_dict = {"login": "Olga", "password": "ab12c5vh4"}
        self.assertIn(server_lib.ServerHandler.message_encode(my_dict), (b'{"login": "Olga", "password": "ab12c5vh4"}',
                                                                         b'{"password": "ab12c5vh4", "login": "Olga"}'))

    def test_message_decode(self):
        my_bytes = b'{"login": "Olga", "password": "ab12c5vh4"}'
        self.assertDictEqual(server_lib.ServerHandler.message_decode(my_bytes),
                             {"login": "Olga", "password": "ab12c5vh4"})

    def test_check_account_name(self):
        account_name = 'asdfghjklasdfghjklasdfghjkl'
        with self.assertRaises(AccountNameError):
            server_lib.ServerHandler.check_account_name(account_name)

    def test_check_server_response(self):
        response_code = '202.2'
        with self.assertRaises(ResponseCodeError):
            server_lib.ServerHandler.check_server_response(response_code)


if __name__ == '__main__':
    unittest.main()
