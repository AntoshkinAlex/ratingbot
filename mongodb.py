from pymongo import MongoClient
from const import MONGODB, MONGODB_LINK

mdb = MongoClient(MONGODB_LINK)[MONGODB]  # переменная для работы с монго


def get_user(user_id):
    user_id = str(user_id)
    try:
        for user in mdb.users.find({"user_id": user_id}):
            return user
    except Exception as err:
        print("Ошибка при взятии пользователя из базы данных", err)


def insert_user(user_id, alias=None):
    user_id = str(user_id)
    old_user = get_user(user_id)
    if alias is not None:
        alias = '@' + alias
    user = {
        "active_name": user_id,
        "alias": alias,
        "birthday": None,
        "codeforces_handle": None,
        "confirmation": {},
        "division": 1,
        "handle": None,
        "is_participant": False,
        "name": '⭕️',
        "notifications": True,
        "user_id": user_id,
    }

    if old_user is not None:
        fields = ['active_name', 'birthday', 'codeforces_handle', 'division', 'handle', 'is_participant', 'name',
                  'notifications', 'confirmation']
        for field in fields:
            if field in old_user:
                user[field] = old_user[field]

    try:
        mdb.users.update_one({"user_id": user_id}, {'$set': user}, upsert=True)
    except Exception as err:
        print("Ошибка при добавлении пользователя в базу данных", err)
    return user


def update_user(user_id, keys):
    user_id = str(user_id)
    try:
        mdb.users.update_one({"user_id": user_id}, {'$set': keys}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении пользователя в базе данных", err)


def delete_user(user_id):
    user_id = str(user_id)
    try:
        mdb.users.delete_many({"user_id": user_id})
    except Exception as err:
        print("Ошибка при удалении пользователя в базе данных", err)


def get_users(params):
    try:
        return mdb.users.find(params)
    except Exception as err:
        print("Ошибка при взятии пользователей из базы данных", err)


def update_contest(contest_id, keys):
    contest_id = str(contest_id)
    try:
        mdb.contests.update_one({"contest_id": contest_id}, {'$set': keys}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении контеста в базе данных", err)


def get_contests():
    return mdb.contests.find({'finished': True}).sort("contest_id")


def get_contest_information(contest_id):
    contest_id = str(contest_id)
    for contest in mdb.contests.find({"contest_id": contest_id}):
        return contest


def update_rating(rating):
    try:
        mdb.rating.update_one({}, {'$set': rating}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении рейтинга в базе данных", err)


def get_rating():
    for rating in mdb.rating.find():
        return rating


def insert_session(chat_id, name, args):
    chat_id = str(chat_id)
    session = {
        "chat_id": chat_id,
        "name": name,
        "args": args
    }
    try:
        mdb.sessions.update_one({"chat_id": chat_id}, {'$set': session}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении сессии", err)


def find_session(chat_id):
    chat_id = str(chat_id)
    for session in mdb.sessions.find({"chat_id": chat_id}):
        return session


def erase_session(chat_id):
    chat_id = str(chat_id)
    mdb.sessions.delete_many({"chat_id": chat_id})


def add_weather(date):
    mdb.weather.delete_many({})
    mdb.weather.insert({"date": date})


def find_weather(date):
    for day in mdb.weather.find({"date": date}):
        return day


def insert_admin(chat_id):
    mdb.admin.insert({"adminId": chat_id})


def find_admin(chat_id):
    chat_id = str(chat_id)
    for admin in mdb.admin.find({"adminId": chat_id}):
        return True
    return False


def delete_admin(chat_id):
    chat_id = str(chat_id)
    mdb.admin.delete_many({"adminId": chat_id})
