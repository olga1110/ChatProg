#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect("messages.db")
cursor = conn.cursor()
#
# cursor.execute('drop table if exists password')
# cursor.execute('drop table if exists messages')
# cursor.execute('drop table if exists chat_messages')
# cursor.execute('drop table if exists op_client')
# cursor.execute('drop table if exists contacts_list')
# cursor.execute('drop table if exists users')
# cursor.execute('drop table if exists groups')
# cursor.execute('drop table if exists users_chat')
#
#
# cursor.execute("""
#
#     create table
#
#         password
#
#         (
#             guid integer primary key autoincrement,
#             h char(64) not null
#          )""")
#
#
# cursor.execute("""
#
#     create table
#
#         users
#
#         (
#             guid integer primary key autoincrement,
#             login text unique not null,
#             level integer not null,
#             password integer references password (guid) not null,
#             date_birth text,
#             city text
#         )
#
#     """)
#
# cursor.execute("""
#
#     create table
#
#         messages
#
#         (
#             guid integer primary key autoincrement,
#             message text,
#             send_time text,
#             user_from integer references users (guid),
#             user_to integer references users (guid)
#         )
#
#     """)
#
# cursor.execute("""
#
#     create table
#
#         chat_messages
#
#         (
#             guid integer primary key autoincrement,
#             chat_name text not null DEFAULT '#chat',
#             message text,
#             send_time text,
#             user_from integer references users (guid)
#
#         )
#
#     """)
#
#
#
# cursor.execute("""
#
#     create table
#
#         op_client
#
#         (
#             guid integer primary key autoincrement,
#             user_id integer references users (guid),
#             ip_adress text,
#             log_time text
#         )
#
#     """)
#
# # списокконтактов (составляется на основании выборки всех записей с id_владельца)
#
# cursor.execute("""
#
#     create table
#
#         contacts_list
#
#         (
#             guid integer primary key autoincrement,
#             owner_id integer references users (guid),
#             user_id integer references users (guid),
#
#             CONSTRAINT constr1 UNIQUE (owner_id, user_id)
#         )
#
#     """)
#
# # Создание группы пользователей (чат)
# cursor.execute("""
#
#     create table
#
#         groups
#
#         (
#             guid integer primary key autoincrement,
#             group_name text unique not null
#
#         )
#
#     """)
#
#
# cursor.execute("""
#
#     create table
#
#         users_chat
#
#         (
#             guid integer primary key autoincrement,
#             group_id references groups (guid),
#             user_id integer references users (guid),
#
#             CONSTRAINT constr1 UNIQUE (group_id, user_id)
#         )
#
#     """)
#
# conn.commit()

# проверка записей
if __name__ == '__main__':
    # cursor.execute("delete from users where login = 'Alex'")
    # conn.commit()
    # cursor.execute("select level from users where login = 'Alex'")
    cursor.execute("select* from groups")
    #
    # # cursor.execute('select* from messages')
    # # cursor.execute('select* from groups')
    # # cursor.execute('select* from contacts_list')
    print(cursor.fetchall())

    login = 'Alex'
    # result = cursor.execute("select p.guid from users as u inner join password as p on u.password = p.guid where u.login = ?", (login,))
    # pid = result.fetchall()[0][0]
    # print(pid)
    # cursor.execute('delete from users where login = ?', login)
    # cursor.execute('delete from password where guid = pid')
    # conn.commit()

    # result = cursor.execute("select p.guid from (select* from users where login = ?) as u inner join password as p on u.password = p.guid", ([login]))
    # print(result.fetchall()[0][0])

# with conn:
#     conn.cursor().execute('select* from users')
    # query = "INSERT OR IGNORE INTO shapes VALUES (?,?);"
    # results = conn.execute(query, ("ID1","triangle"))

# Менеджер контекста------------------------------------------------
class CWith():
    def __init__(self, engine):

        # self.conn = sqlite3.connect("messages.db")
        # self.cursor = self.conn.cursor()
        self.engine = engine
        self.session = sessionmaker(bind=engine)()


    # def __iter__(self):
    #     for item in self.cursor:
    #         yield item

    def __enter__(self):
        return self.session

    def __exit__(self, err, value, traceback):
        if isinstance(err, Exception):
            self.conn.rollback()
        # elif sqlite3.IntegrityError:
        #     print('Транзакция отклонена')
        else:
            self.conn.commit()



# conn = CWith()

# with conn as cursor:
#
#     cursor.execute("insert or ignore into groups values(52, 'test2')")
#     cursor.execute("insert or ignore into groups values(11, 'test1')")
# #     cursor.update(...)
#
# with conn as cursor:
#
# cursor.execute("delete from groups where group_name = 'test'")
# conn.commit()
#     print('Done')

cursor.execute("select* from users")
print(cursor.fetchall())