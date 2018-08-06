import unittest
from unittest.mock import Mock
import LIB.client_lib
import time


class CTestClientLib(unittest.TestCase):
    def test_client(self):
        data = {
            'action': 'presence',
            'time': time.time(),
            'type': 'status',
            'user': {
                'account_name': 'account_name',
                'status': 'status'
            }
        }
        data_buf = client_lib.message_encode(data)
        data_server = {'response': '202','alert': 'Login is accepted'}
        data_server_buf = client_lib.message_encode(data_server)
        virt_sock = Mock()
        virt_sock.send.return_value = data_buf
        virt_sock.recv.return_value = data_server_buf
        result = client_lib.main_loop_for_client(virt_sock, data)
        self.assertDictEqual(result, {'response': '202','alert': 'Login is accepted'})

    def test_client_mes_read(self):
        data = {
            'action': 'msg',
            'time': time.time(),
            'to': "#chat",
            'from': 'account_name',
            'message': 'msg'
        }
        data_buf = client_lib.message_encode(data)
        virt_sock = Mock()
        virt_sock.recv.return_value = data_buf
        virt_sock.send.return_value = None
        result = client_lib.client_mes_read(virt_sock)
        self.assertDictEqual(result, data)

    def test_client_mes_write(self):
        account_name = 'Olga'
        msg = 'msg'
        data = {
            'action': 'msg',
            'time': time.time(),
            'to': '#chat',
            'from': account_name,
            'message': 'msg'
        }
        data_buf = client_lib.message_encode(data)
        virt_sock = Mock()
        virt_sock.recv.return_value = None
        virt_sock.send.return_value = data_buf
        result = client_lib.client_mes_write(virt_sock, msg, account_name)
        self.assertDictEqual(result, data)

if __name__ == '__main__':
    unittest.main()

