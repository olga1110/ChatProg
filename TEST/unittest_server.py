import unittest
from unittest.mock import Mock
import os
import sys
import time

os.chdir('..')
sys.path.append(os.path.join(os.getcwd(), 'LIB'))
import server_lib



class CTestLib(unittest.TestCase):
    def test_server(self):
        data = {
            'action': 'presense',
            'time': time.time(),
            'type': 'status',
            'user': {
                'account_name': 'account_name',
                'status': 'status'
            }
        }


        virt_sock = Mock()
        virt_sock.send.return_value = None
        # data_buf = server_lib.message_encode(data)
        virt_sock.recv.return_value = data
        response = server_lib.JIMResponse(data)
        result = response.get_server_response()
        self.assertDictEqual(result, {'response': 202,'alert': 'Login is accepted'})

if __name__ == '__main__':
    unittest.main()
