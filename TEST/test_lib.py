import unittest
import os
import sys
import time


os.chdir('..')
sys.path.append(os.path.join(os.getcwd(), 'LIB'))
import server_lib
from errors import AccountNameError, ResponseCodeError





class TestLib(unittest.TestCase):

    def test_message_encode(self):
        my_dict = {"login": "Olga", "password": "ab12c5vh4"}
        self.assertIn(server_lib.message_encode(my_dict),(b'{"login": "Olga", "password": "ab12c5vh4"}', b'{"password": "ab12c5vh4", "login": "Olga"}'))

    def test_message_decode(self):
        my_bytes = b'{"login": "Olga", "password": "ab12c5vh4"}'
        self.assertDictEqual(server_lib.message_decode(my_bytes), {"login": "Olga", "password": "ab12c5vh4"})

    def test_check_presence_message(self):
        presense_message = {
        'action': 'presence',
        'type': 'status',
        'user': {'status': 'online'}
            }
        self.assertDictEqual(server_lib.check_presence_message(presense_message), {'response': '400', 'error': 'Wrong request/JSON-object'})
        presense_message['time'] = time.time()
        presense_message['user']['account_name'] = 'account_name'
        self.assertDictEqual(server_lib.check_presence_message(presense_message), {'response': '202','alert': 'Login is accepted'})

    def test_check_account_name(self):
        account_name = 'asdfghjklasdfghjklasdfghjkl'
        with self.assertRaises(AccountNameError):
            server_lib.check_account_name(account_name)

        def check_server_response(result):
            if len(result) != 3:
                raise ResponseCodeError(result)

    def test_check_server_response(self):
        response_code = '202.2'
        with self.assertRaises(ResponseCodeError):
            server_lib.check_server_response(response_code)

if __name__ == '__main__':
    print(os.path.join(os.getcwd(), 'LIB'))
    unittest.main()



