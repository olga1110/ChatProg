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
    # cursor.execute('select* from users')
    # cursor.execute('select* from messages')
    # cursor.execute('select* from op_client')
    cursor.execute('select* from contacts_list')
    print(cursor.fetchall())

