import unittest
from unittest.mock import Mock
import LIB.server_lib
import time


class CTestLib(unittest.TestCase):
    def test_server(self):
        data = {
            'action': 'presence',
            'time': time.time(),
            'type': 'status',
            'user': {
                'account_name': 'account_name',
                'status': 'status'
            }
        }
        data_buf = server_lib.message_encode(data)

        virt_sock = Mock()
        virt_sock.send.return_value = None
        virt_sock.recv.return_value = data_buf
        result = server_lib.main_loop_for_server(virt_sock)
        self.assertDictEqual(result, {'response': '202','alert': 'Login is accepted'})

if __name__ == '__main__':
    unittest.main()
