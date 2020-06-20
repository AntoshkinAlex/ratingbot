import const
import mongodb as backend
from telebot import types

bot = const.bot

def print_admin_user_information(chatId, user):
    try:
        user_id = const.users_handles[user]
        backend.insert_user(user_id)
        userInformation = backend.get_user(user_id)
        userAchievements = const.userAchievements[user]
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Сменить дивизион", callback_data="change_div " + user_id)
        but_2 = types.InlineKeyboardButton(text="Добавить участника", callback_data="add_user " + user_id)
        but_3 = types.InlineKeyboardButton(text="Добавить личные достижения", callback_data="add_achievements " + user_id)
        key.add(but_1)
        key.add(but_2)
        key.add(but_3)
        is_participant = "Да"
        if userInformation['is_participant'] == False:
            is_participant = "Нет"
        bot.send_message(chatId, "<b>" + userInformation['name'] + ":</b>\n\n" +
                "Дивизион:\n" + str(userInformation['division']) + "\n\n" +
                "Достижения:\n" + userInformation['achievements'] + "\n" + userAchievements + "\n" +
                "Является участником контестов: " + is_participant + "\n",
                parse_mode="html", reply_markup=key)
    except Exception as err:
        print('Ошибка при выводе личной информации админу', err)
        bot.send_message(chatId, "Произошла ошибка")


def change_div(message, chat_id):
    try:
        user_id = message[message.find('change_div ') + 11: len(message)]
        backend.insert_user(user_id)
        user = backend.get_user(user_id)
        newdiv = 1
        if user['division'] == 1:
            newdiv = 2
        backend.update_user(user_id, {'division': newdiv})
        print_admin_user_information(chat_id, const.users_id[user_id])
    except Exception as err:
        print('Не удалось сменить дивизион пользователя', err)
        bot.send_message(chat_id, 'Не удалось сменить дивизион пользователя')
