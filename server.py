
import argparse
import socketserver
import sys
import time
import select
from socket import socket, AF_INET, SOCK_STREAM
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from threading import Thread, RLock
from queue import Queue
from Crypto.PublicKey import RSA
import ssl
from secrets import token_urlsafe
from LIB.errors import AccountNameError, ResponseCodeError
from LIB.server_lib import *
from DB.DB_classes import *


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--host', help='server address', nargs='?', const='')
parser.add_argument('--port', nargs='?', const=7777, type=int)
args = parser.parse_args('--host --port'.split())
host = args.host
port = args.port

# Подключение к базе данных
# engine = create_engine('sqlite:///messages.db')
# session = sessionmaker(bind=engine)()


class HandleThread(Thread):
    def __init__(self, serv_sock, sock, addr, data):

        super().__init__(daemon=True, target=self.run)

        self.serv_sock = serv_sock
        # self.msg_queues = msg_queues
        # print(msg_queues)
        self.sock = sock
        self.addr = addr
        # self.users = users
        self.inputs = []
        self.outputs = []
        self.handler = ServerHandler()
        self.data = data
        self.start()

    def run(self):
        print('Новый поток создан для клиента' + str(self.addr))
        self.inputs = [self.sock]
        self.outputs = [self.sock]
        while self.inputs:
            try:
                r, w, e = select.select(self.inputs, self.outputs, [], 5)
            except OSError as e:
                pass
                # self.disconnect()
                # break

            if self.sock in r:
                try:
                    msg_buf = self.sock.recv(4096)
                    msg = message_decode(msg_buf)
                    login = self.data['user']['account_name']
                except OSError as e:
                    pass
                    # self.disconnect()
                    # break

                if msg['action'] == 'msg':
                    if msg['type'] == 'chat':
                        self.handler.insert_chat_messages(login, msg['session'], self.serv_sock.sessions, msg)
                        for c in self.serv_sock.msg_queues:  # Обходим все очереди сообщений
                            if c != self.sock:  # Кроме очереди текущего сокета
                                self.serv_sock.msg_queues[c].put(msg_buf)
                    elif msg['type'] == 'personal':
                        login_to = msg['to']
                        print(login_to)
                        print(self.serv_sock.users[login_to])
                        self.serv_sock.msg_queues[self.serv_sock.users[login_to]].put(msg_buf)
                        print(self.serv_sock.msg_queues)
                        # msg_snd = message_encode(msg)
                        self.handler.insert_messages(login, msg['session'], self.serv_sock.sessions, msg)

                elif msg['action'] == 'get_key':
                    pub_key = self.serv_sock.keys[msg['user_login']]
                    print(pub_key)
                    self.sock.send(pub_key.exportKey(format='PEM', passphrase=None, pkcs=1))
                elif msg['action'] == 'get_contacts':
                    if msg:
                        print('Получен запрос на отправку списка контактов: {}'.format(msg))
                        client_contacts = ListContacts(self.data).get_client_contacts(self.sock, login, msg['session'], self.serv_sock.sessions)
                        # client_contacts_snd = message_encode(client_contacts)
                        # self.sock.send(client_contacts_snd)
                        # ListContacts(self.data).send_client_contacts(self.sock, login)
                elif msg['action'] == 'add_contact' or msg['action'] == 'del_contact':
                    print('Пользовательский запрос на изменение контактов: {}'.format(msg))
                    ListContacts(self.data).modify_contact(self.sock, login, msg['session'], self.serv_sock.sessions, msg['action'], msg['user_id'])
                elif msg['action'] == 'create_chat':
                    self.handler.create_chat(self.sock, login, msg['session'], self.serv_sock.sessions, msg)

                    # create_chat_response_snd = message_encode(create_chat_response)
                    # self.sock.send(create_chat_response_snd)

            if self.sock in w:

                if not self.serv_sock.msg_queues[self.sock].empty():
                    data = self.serv_sock.msg_queues[self.sock].get()
                    try:
                        # sent by socket directly
                        self.sock.send(data)
                    except OSError as e:
                        pass
                        # self.disconnect()
                        # break


class Server(Thread, metaclass=Singleton):
    def __init__(self, host, port):
        super().__init__(daemon=True, target=self.run)
        self.sock = socket(AF_INET, SOCK_STREAM)
        # self.sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM), ciphers="AES128-SHA")
        self.host = host
        self.port = port
        self.address = (str(self.host), int(self.port))
        self.msg_queues = {}
        self.users = {}
        self.lock = RLock()
        self.keys = {}
        self.sessions = {}
        self.handler = ServerHandler()
        # self.shutdown = False
        try:
            self.sock.bind(self.address)
            self.sock.listen(7)
            self.sock.settimeout(3)
            self.start()
        except OSError as e:
            pass  # timeout вышел
        # except self.sock.error:
        #     self.shutdown = True
        while True:
            # waiting for cmd
            msg = input()
            if msg == 'quit':
                for sock in self.connection_list:
                    sock.close()
                self.shutdown = True
                self.server_socket.close()

    def run(self):
        clients = []
        while True:
            # with self.lock:
            try:
                conn, addr = self.sock.accept()  # Проверка подключений
                # conn = ssl.wrap_socket(conn, ciphers="AES128-SHA")
                print('Получен запрос на соединение с %s' % str(addr))
                # получение publickey клиента

                pub_key = RSA.importKey((conn.recv(1024).decode()), passphrase=None)
                print(pub_key)
                # self.keys[conn] = key
                while True:
                    data_buf = conn.recv(1024)
                    if data_buf:
                        data = message_decode(data_buf)
                        # Запрос на регистрацию пользователя
                        if data['action'] == 'register':
                            result = self.handler.create_registr_response(conn, data)
                            if result['response'] == 200:
                                self.handler.insert_new_user(data)
                    # Запрос на авторизацию (presense)
                        if data['action'] == 'presense':
                            result = self.handler.create_presense_response(conn, data)
                            if result['response'] == 400 or result['response'] == 402:
                                print('Клиенту отказано в подключении: {}'.format(result))
                            else:
                                print('Клиент подключен: {}'.format(result))
                                login = data['user']['account_name']
                                self.users[login] = conn
                                clients.append(conn)

                            # генерируем идентификатор сессии
                                self.sessions[login] = token_urlsafe(64)
                                conn.send(self.sessions[login].encode('utf-8'))

                                # self.keys[login] = pub_key
                                # print(self.keys)
                            #  вставка в табл.op_client
                                self.handler.insert_op_client(login, addr[0], data['time'])
                                self.msg_queues[conn] = Queue()
                                # словарь клиент - открытый ключ
                                self.keys[login] = pub_key
                                print(self.keys)

                                HandleThread(self, conn, addr, data)
                                break
                    else:
                        break
            except OSError as e:
                pass  # timeout вышел


if __name__ == '__main__':
    sock = Server(host, port)
# sock.mainloop()





