from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from DB_classes import*


engine = create_engine('sqlite:///messages.db')
# engine = create_engine('sqlite:///messages.db', echo=True)
session = sessionmaker(bind=engine)()


# Добавление пользователей в БД
user_1 = CUsers(login='user_1', password='user1', city='Perm')
user_2 = CUsers(login='user_2', password='user2', city='Moskva')
user_3 = CUsers(login='user_3', password='user3', city='Peterburg')
user_4 = CUsers(login='user_4', password='user4', city='Peterburg')
user_5 = CUsers(login='user_5', password='user5', city='Anapa')
user_6 = CUsers(login='user_6', password='user6', city='Ekaterburg')
user_7 = CUsers(login='user_7', password='user7', city='Kyrgan')

session.add_all()
session.commit()

# Заполнение contacts_list на основе messages
engine.execute("delete from contacts_list")
result = engine.execute("select* from users")
for owner in result.fetchall():
    result1 = engine.execute(
        "select distinct user_to from messages where user_from = ? union select distinct user_from from messages "
        "where user_to = ?", (owner[0], owner[0]))
    for user in result1.fetchall():
        session.add(CContactsList(owner_id=owner[0], user_id=user[0]))
        session.commit()


