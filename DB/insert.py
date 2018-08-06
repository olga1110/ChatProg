from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from DB_classes import*


engine = create_engine('sqlite:///messages.db')
# engine = create_engine('sqlite:///messages.db', echo=True)
session = sessionmaker(bind=engine)()


# Добавление пользователей в БД
# user_1 = CUsers(login='user_1', password='user1', city='Perm')
# user_2 = CUsers(login='user_2', password='user2', city='Moskva')
# user_3 = CUsers(login='user_3', password='user3', city='Peterburg')
# user_4 = CUsers(login='user_4', password='user4', city='Peterburg')
# user_5 = CUsers(login='user_5', password='user5', city='Anapa')
# user_6 = CUsers(login='user_6', password='user6', city='Ekaterburg')
# user_7 = CUsers(login='user_7', password='user7', city='Kyrgan')
#
# session.add(user_1)
# session.add(user_2)
# session.add(user_3)
# session.add(user_4)
# session.add(user_5)
# session.add(user_6)
# session.add(user_7)
#
# session.commit()
# ----------------------------------------------------------------------------------------------------
# Заполнение contacts_list на основе messages
engine.execute("delete from contacts_list")
result = engine.execute("select* from users")
for owner in result.fetchall():
    result1 = engine.execute(
        "select distinct user_to from messages where user_from = ? union select distinct user_from from messages where user_to = ?", (owner[0], owner[0]))
    for user in result1.fetchall():
        session.add(CContactsList(owner_id=owner[0], user_id=user[0]))
        session.commit()


# ----------------------------------------------------------------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ЗАПРОСЫ
# user1 = 'user_1'
# result = engine.execute("select password from users where login = ?",(user1))
#
# # result = engine.execute("select password from users where login = 'user_1'")
# print(result.fetchall()[0][0])
# print(result == 'user1')

# result = session.query(CUsers).filter_by(guid = 1).all()
# print(result)


# guid = Column(Integer(), primary_key=True)
# user_id = Column(Integer(), ForeignKey('users.guid'))
# ip_adress = Column(Unicode(), nullable=False)
# log_time = Column(Unicode(), nullable=False)
#
# data = {
#     'action': 'presence',
#     'time': time.time(),
#     'type': 'status',
#     'user': {
#         'account_name': 'account_name',
#         'status': 'status'
#     }
# }
#
#
# # user_1 = CUsers(user_id='user_1', ip_adress=, log_time= data['time'])
# session.add(user_1)
# session.commit()

# result = engine.execute("select* from op_client")
# for line in result.fetchall():
#     print(line)
#
# result = engine.execute("select* from messages")
# for line in result.fetchall():
#     print(line)
#
# result = engine.execute("select* from contacts_list")
# for line in result.fetchall():
#     print(line)

