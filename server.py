import sys
import os
# sys.path.append(os.path.join(os.getcwd(), 'DB'))
# sys.path.append(os.path.join(os.getcwd(), 'LIB'))

import argparse
import socketserver
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

path_db = os.path.join(os.getcwd(), 'DB', 'messages.db')
engine = create_engine('sqlite:///' + path_db)
session = sessionmaker(bind=engine)()


class Server(Thread, metaclass=Singleton):
    def __init__(self, host, port, session, engine):
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
        self.handler = ServerHandler(session, engine)
        self._db = ServerDB(session, engine)

        # self.shutdown = False
        try:
            self.sock.bind(self.address)
            self.sock.listen()
            self.sock.settimeout(3)
            self.start()
        except OSError as e:
            pass  # timeout вышел
        # except self.sock.error:
        #     self.shutdown = True
        while True:
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

                while True:
                    data_buf = conn.recv(1024)
                    if data_buf:
                        data = ServerHandler.message_decode(data_buf)
                        # Запрос на регистрацию пользователя
                        if data['action'] == 'register':
                            result = self.handler.create_registr_response(data)
                            if result['response'] == 200:
                                self._db.insert_new_user(data)
                            self.handler.send_response_to_client(conn, result)

                    # Запрос на авторизацию (presence)
                        if data['action'] == 'presence':
                            result = self.handler.create_presence_response(data)
                            self.handler.send_response_to_client(conn, result)
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
                                self._db.insert_op_client(login, addr[0], data['time'])
                                self.msg_queues[conn] = Queue()
                                # словарь клиент - открытый ключ
                                self.keys[login] = pub_key
                                print(self.keys)
                                HandleThread(self, conn, addr, data, session, engine)
                                break
                    else:
                        break
            except OSError as e:
                pass  # timeout вышел


class HandleThread(Thread):
    def __init__(self, serv_sock, sock, addr, data, session, engine):

        super().__init__(daemon=True, target=self.run)
        self.serv_sock = serv_sock
        # self.msg_queues = msg_queues
        # print(msg_queues)
        self.sock = sock
        self.addr = addr
        # self.users = users
        self.inputs = []
        self.outputs = []
        self.data = data
        self.list_contacts = ListContacts(self.data, session, engine)
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
                    print(msg_buf)
                    msg = ServerHandler.message_decode(msg_buf)
                    login = self.data['user']['account_name']
                except OSError as e:
                    pass
                    # self.disconnect()
                    # break

                if msg['action'] == 'msg':
                    if msg['type'] == 'chat':
                        self.serv_sock._db.insert_chat_messages(login, msg['session'], self.serv_sock.sessions, msg)
                        for c in self.serv_sock.msg_queues:  # Обходим все очереди сообщений
                            if c != self.sock:  # Кроме очереди текущего сокета
                                self.serv_sock.msg_queues[c].put(msg_buf)
                    elif msg['type'] == 'personal':
                        login_to = msg['to']
                        self.serv_sock.msg_queues[self.serv_sock.users[login_to]].put(msg_buf)
                        self.serv_sock._db.insert_messages(login, msg['session'], self.serv_sock.sessions, msg)

                elif msg['action'] == 'get_key':
                    pub_key = self.serv_sock.keys[msg['user_login']]
                    print(pub_key)
                    self.sock.send(pub_key.exportKey(format='PEM', passphrase=None, pkcs=1))
                elif msg['action'] == 'get_contacts':
                    if msg:
                        print('Получен запрос на отправку списка контактов: {}'.format(msg))
                        client_contacts = self.list_contacts.get_client_contacts(login, msg['session'], self.serv_sock.sessions, self.sock)
                        # client_contacts_snd = message_encode(client_contacts)
                        # self.sock.send(client_contacts_snd)
                        # self.list_contacts.send_client_contacts(self.sock, login)
                elif msg['action'] == 'add_contact' or msg['action'] == 'del_contact':
                    print('Пользовательский запрос на изменение контактов: {}'.format(msg))
                    result = self.list_contacts.modify_contact(login, msg['session'], self.serv_sock.sessions, msg['action'], msg['user_id'])
                    ServerHandler.send_response_to_client(self.sock, result)
                elif msg['action'] == 'create_chat':
                    result = self.list_contacts.create_chat(login, msg['session'], self.serv_sock.sessions, msg)
                    ServerHandler.send_response_to_client(self.sock, result)

            if self.sock in w:

                if not self.serv_sock.msg_queues[self.sock].empty():
                    data = self.serv_sock.msg_queues[self.sock].get()
                    print(data)
                    try:
                        # sent by socket directly
                        self.sock.send(data)
                        print('Сообщение отправлено клиенту!')
                    except OSError as e:
                        pass
                        # self.disconnect()
                        # break


if __name__ == '__main__':
    sock = Server(host, port, session, engine)
# sock.mainloop()





