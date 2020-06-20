from pymongo import MongoClient
from const import MONGODB, MONGODB_LINK
import const

mdb = MongoClient(MONGODB_LINK)[MONGODB]  # переменная для работы с монго


def insert_user(user_id):
    handle = ""
    user_id = str(user_id)
    is_participant = False
    division = 1
    old_user = get_user(user_id)
    if old_user is not None and 'division' in old_user:
        is_participant = old_user['is_participant']
        division = old_user['division']
    if user_id in const.users_id:
        handle = const.users_id[user_id]
        is_participant = True
    user = {
        "user_id": user_id,
        "handle": handle,
        "is_participant": is_participant,
        "division": division
    }
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


def get_users():
    return mdb.users.find({"is_participant": True})


def get_user(user_id):
    try:
        user_id = str(user_id)
        for user in mdb.users.find({"user_id": user_id}):
            return user
    except Exception as err:
        print("Ошибка при взятии пользователя из базы данных", err)


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