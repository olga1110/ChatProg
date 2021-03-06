#!/usr/bin/env python3

from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

CBase = declarative_base()


class CPassword(CBase):
    __tablename__ = 'password'

    guid = Column(Integer(), primary_key=True)
    h = Column(Unicode(), nullable=False)

    def __repr__(self):
        return 'CUsers<guid = %d, h = %s>' % (self.guid, self.h)


class CUsers(CBase):
    __tablename__ = 'users'

    guid = Column(Integer(), primary_key=True)
    login = Column(Unicode(), nullable=False)
    level = Column(Integer(), nullable=False)
    password = Column(Integer(), ForeignKey('password.guid'))
    date_birth = Column(Unicode())
    city = Column(Unicode())

    check_1 = UniqueConstraint('login')

    def __repr__(self):
        return 'CUsers<guid = %d, login = %s, level = %d, password = %d, date_birth = %s, city = %s>' % (
        self.guid, self.login, self.level, self.password, self.date_birth, self.city)


class CMessages(CBase):
    __tablename__ = 'messages'

    guid = Column(Integer(), primary_key=True)
    message = Column(Unicode())
    send_time = Column(Unicode())
    user_from = Column(Integer(), ForeignKey('users.guid'))
    user_to = Column(Integer(), ForeignKey('users.guid'))

    p_user_from = relationship('CUsers', foreign_keys=[user_from])
    p_user_to = relationship('CUsers', foreign_keys=[user_to])

    def __repr__(self):
        return "CMessages<guid = %d, user_from = %d, user_to = %d, message = %s, send_time = %s>" % (
        self.guid, self.user_from, self.user_to, self.message, self.send_time)


class CChatMessages(CBase):
    __tablename__ = 'chat_messages'

    guid = Column(Integer(), primary_key=True)
    chat_name = Column(Unicode(), nullable=False, default='#chat')
    message = Column(Unicode())
    send_time = Column(Unicode())
    user_from = Column(Integer(), ForeignKey('users.guid'))

    p_user_from = relationship('CUsers', foreign_keys=[user_from])

    def __repr__(self):
        return "CMessages<guid = %d, chat_name = %s, user_from = %d, message = %s, send_time = %s>" % (
        self.guid, self.chat_name, self.user_from, self.message, self.send_time)


class COpClient(CBase):
    __tablename__ = 'op_client'

    guid = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.guid'))
    ip_adress = Column(Unicode(), nullable=False)
    log_time = Column(Unicode(), nullable=False)

    p_user_id = relationship('CUsers', foreign_keys=[user_id])

    def __repr__(self):
        return "CMessages<guid = %d, user_id = %d, ip_adress = %s, log_time = %s>" % (
        self.guid, self.user_id, self.ip_adress, self.log_time)


class CContactsList(CBase):
    __tablename__ = 'contacts_list'

    guid = Column(Integer(), primary_key=True)
    owner_id = Column(Integer(), ForeignKey('users.guid'))
    user_id = Column(Integer(), ForeignKey('users.guid'))

    p_owner_id = relationship('CUsers', foreign_keys=[user_id])
    p_user_id = relationship('CUsers', foreign_keys=[user_id])

    check_1 = UniqueConstraint('owner_id', 'user_id')

    def __repr__(self):
        return "CContactsList<guid = {}, owner_id = {}, user_id = {}>".format(self.guid, self.owner_id, self.user_id)


class CGroups(CBase):
    __tablename__ = 'groups'

    guid = Column(Integer(), primary_key=True)
    group_name = Column(Unicode(), nullable=False)

    check_1 = UniqueConstraint('group_name')

    def __repr__(self):
        return 'CUsers<guid = %d, group_name = %s>' % (self.guid, self.group_name)


class CUsersChat(CBase):
    __tablename__ = 'users_chat'

    guid = Column(Integer(), primary_key=True)
    group_id = Column(Integer(), ForeignKey('groups.guid'))
    user_id = Column(Integer(), ForeignKey('users.guid'))

    p_user_id = relationship('CUsers', foreign_keys=[user_id])
    p_group_id = relationship('CGroups', foreign_keys=[group_id])

    check_2 = UniqueConstraint('group_id', 'user_id')

    def __repr__(self):
        return 'CUsers<guid = %d, group_id = %d, user_id = %d>' % (self.guid, self.group_id, self.user_id)


# class CWith():
#     def __init__(self, engine):
#
#         # self.conn = sqlite3.connect("messages.db")
#         # self.cursor = self.conn.cursor()
#         self.engine = engine
#         self.session = sessionmaker(bind=engine)()
#
#
#     # def __iter__(self):
#     #     for item in self.cursor:
#     #         yield item
#
#     def __enter__(self):
#         return self.session
#
#     def __exit__(self, err, value, traceback):
#         if isinstance(err, Exception):
#             self.conn.rollback()
#         # elif sqlite3.IntegrityError:
#         #     print('Транзакция отклонена')
#         else:
#             self.conn.commit()
# conn = CWith()


if __name__ == '__main__':
    import os
    import sys

    # engine = create_engine('sqlite:///messages.db')
    # engine = create_engine('sqlite:///messages.db', echo=True)
    sys.path.append(os.path.join(os.getcwd(), 'DB'))
    path_db = os.path.join(os.getcwd(), 'DB', 'messages.db')
    path_db1 = 'sqlite:///' + path_db
    engine = create_engine(path_db1)
    session = sessionmaker(bind=engine)()

    # with conn as cursor:
    #
    #     cursor.execute("insert or ignore into groups values(52, 'test2')")
    #     cursor.execute("insert or ignore into groups values(11, 'test1')")
    # #     cursor.update(...)

    data = 'Olga'
    result = session.query(CUsers).filter_by(login=data).all()
    print(result.fetchall()[0][0])
