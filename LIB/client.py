from socket import *
import sys
import time
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from Crypto.PublicKey import RSA
import ssl
import LIB.client_lib as client_lib
from DB.DB_classes import *


class Singleton(type):

    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class Client(metaclass=Singleton):
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        # self.s = ssl.wrap_socket(self.s, ciphers="AES128-SHA")
        self.s.connect((addr, port))

     # presense-сообщение
    def get_account_name(self, user_name):
    #     user_name = input('Введите ваш логин: ')
    #     while user_name == '':
    #         user_name = input('Введите ваш логин: ')
        account_name = client_lib.CCls().account_name
        account_name = user_name
        return account_name

    def get_user_status(self):
        # user_status = input('Ваш статус - online? (Y/N)')
        user_status = 'Y'
        return user_status

    def get_register_response(self, account_name, level, password, password1):
        data = client_lib.RegisterMessage(account_name, 'register', 'registration', level, password, password1).get_client_message()
        print(data)
        server_response = client_lib.main_loop_for_client(self.s, data)
        return server_response

    def get_presense_response(self, account_name, user_status, level, password):
        data = client_lib.PresenseMessage(account_name, 'presense', 'status', user_status, level, password).get_client_message()
        server_response = client_lib.main_loop_for_client(self.s, data)
        return server_response


class Chat:
    def __init__(self, sock):
        self.s = sock
    def read_client_message(self):
        input_message = client_lib.client_mes_read(self.s)
        return input_message

    def client_write_chat(self, msg, account_name, session):
        msg_chat = client_lib.client_write_chat(self.s, msg, account_name, session)
        return msg_chat

    def client_write_person(self, msg, to, account_name, session):
        personal_message = client_lib.client_write_person(self.s, msg, to, account_name, session)
        return personal_message

    # def get_client_key(self, to, msg):
    # def get_client_key(self, to):
    #     request_key = {'action': 'get_key', 'user_login': to}
    #     print(request_key)
    #     self.s.send(client_lib.message_encode(request_key))
    #     # # user_key = self.s.recv(1024)
    #     # # msg_bytes = client_lib.message_encode(msg)
    #     # pub_key = RSA.importKey((self.s.recv(1024).decode()), passphrase=None)
    #     # return rsa.encrypt(msg_bytes, pub_key)
    #     return RSA.importKey((self.s.recv(1024).decode()), passphrase=None)



class ListContacts:
    def __init__(self, sock):
        self.s = sock

    def client_get_contacts(self, session):
        request = client_lib.get_contacts(self.s, session)
        return request

    def read_server_response_contacts(self):
        server_response_contacts = client_lib.read_server_response_contacts(self.s)
        return server_response_contacts

    def get_request_modify(self, action, nickname, session):
        request = client_lib.get_request_modify(self.s, action, nickname, session)
        return request

    def create_chat(self, chat_name, users_id, session):
        request = client_lib.create_chat(self.s, chat_name, users_id, session)
        return request



if __name__ == '__main__':

    # Подключение клиента
    try:
        addr = sys.argv[2]
    except IndexError:
        addr = 'localhost'

    try:
        port = int(sys.argv[3])
    except IndexError:
        port = 7777
    except ValueError:
        print('Задайте целочисленное значение для порта')
        sys.exit(0)


    try:
        if sys.argv[1] in ('r', 'w'):
            mode = sys.argv[1]
    except IndexError:
        # открываем по умолчанию на чтение
        mode = 'r'


    if mode == 'w':
        mode_to_form = 'Запись'
    else:
        mode_to_form = 'Чтение'



    s = Client(addr, port)



    # account_name = s.get_account_name(user_name)
    # account_name = user_name

    user_status = s.get_user_status()


    # Подключение к базе данных
    engine = create_engine('sqlite:///clients_messages.db')
    session = sessionmaker(bind=engine)()

    # presense-сообщение и ответ сервера
    result = s.get_server_response()
    print('Ответ от сервера получен: {}'.format(result))


    # Общий чат
    chat_client = Chat(s.s)

    # Работа со списком контактов
    list_contacts = ListContacts(s.s)

    # Работа со списком контактов
    modify_request = 'Y'
    while modify_request == 'Y':
        contacts_list = input("Для получения списка контактов нажмите 'L'/ \n"
                                     "Для добавления контакта нажмите 'A'/\n"
                                     "Для удаления контакта нажмите 'D'/\n"
                                      "Для создания чата нажмите 'C'/\n"
                                     "Для перехода в основной режим нажмите любую клавишу: ")
        # Вывод списка контактов
        if contacts_list == 'L':
            list_contacts.client_get_contacts(session)
            count = list_contacts.read_server_response_contacts()
            print('Ваш список контактов:')
            for _ in range(count):
                list_contacts.read_server_response_contacts()
        #Запрос на добавление/удаление контактов
        elif contacts_list == 'A' or contacts_list == 'D':
            nickname = input("Введите логин для добавления/удаления пользователя: ")
            if contacts_list == 'A':
                action = 'add_contact'
            elif contacts_list == 'D':
                action = 'del_contact'
            list_contacts.get_request_modify(action, nickname, session)
            server_response_rcv = s.s.recv(4096)
            server_response = client_lib.message_decode(server_response_rcv)
            if server_response['response'] == '202':
                print('Операция выполнена успешно')
            else:
                print(server_response['error'])

        elif contacts_list == 'C':
            # Создание группы
            users_id = []
            chat_name = input("Задайте имя чата: ")
            while chat_name == '':
                chat_name = input("Задайте имя чата: ")
            add_user = 'Y'
            while add_user == 'Y':
                user_id = input('Для добавления в чат пользователя введите логин: ')
                users_id.append(user_id)
                add_user = input('Добавить нового пользователя,(Y/N)?')
            chat_client.create_chat(chat_name, users_id)
            server_response_rcv = s.s.recv(4096)
            server_response = client_lib.message_decode(server_response_rcv)
            print(server_response)
        modify_request = input("Продолжить работу со списком контактов,(Y/N)?")

    #Режим мессенджера
    if mode == 'r':
        while True:  # Постоянный опрос сервера
            # client_lib.client_mes_read(s)
            chat_client.read_client_message()

    if mode == 'w':
        while True:
            msg = input("Введите сообщение: ")
            chat = input('Сообщение для чата? (Y/N)')
            if chat != 'Y':
                chat = 'N'
            if chat == 'N':
                to = input("Кому доставить сообщение? Введите логин: ")
                chat_client.client_write_person(msg, to, account_name, session)
            else:
                chat_client.client_write_chat(msg, account_name, session)


    s.close()





