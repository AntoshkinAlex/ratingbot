from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import const
import mongodb as backend

bot = const.bot

def print_admin_user_information(chatId, user):
    try:
        user_id = user
        userInformation = backend.get_user(user_id)
        userAchievements = '\n'
        if 'custom_achievements' in userInformation:
            userAchievements = ''
            for achievement in userInformation['custom_achievements']:
                userAchievements += str(achievement) + '\n'
        key = InlineKeyboardMarkup()
        but_1 = InlineKeyboardButton(text="Изменить дивизион", callback_data="change_div " + user_id)
        but_2 = InlineKeyboardButton(text="Изменить состояние участника контестов", callback_data="change_participant " + user_id)
        but_3 = InlineKeyboardButton(text="Изменить личные достижения", callback_data="show_achievements " + user_id)
        key.add(but_1)
        key.add(but_2)
        key.add(but_3)
        is_participant = "Да"
        if not userInformation['is_participant']:
            is_participant = "Нет"
        bot.send_message(chatId, "<b>" + userInformation['active_name'] + ":</b>\n\n" +
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
        user = backend.get_user(user_id)
        newdiv = 1
        if user['division'] == 1:
            newdiv = 2
        backend.update_user(user_id, {'division': newdiv})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось сменить дивизион пользователя', err)
        bot.send_message(chat_id, 'Не удалось сменить дивизион пользователя')


def change_participant(message, chat_id):
    try:
        user_id = message[message.find('change_participant ') + 19: len(message)]
        user = backend.get_user(user_id)
        newparticipant = True
        if user['is_participant']:
            newparticipant = False
        backend.update_user(user_id, {'is_participant': newparticipant})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось поменять состояние участника контеста', err)
        bot.send_message(chat_id, 'Не удалось поменять состояние участника контеста')


def show_achievements(message, chat_id):
    try:
        user_id = message[message.find('show_achievements ') + 18: len(message)]
        user = backend.get_user(user_id)
        custom_achievements = []
        if 'custom_achievements' in user:
            custom_achievements = user['custom_achievements']

        key = InlineKeyboardMarkup()
        for (index, achievement) in enumerate(custom_achievements):
            button = InlineKeyboardButton(text=achievement, callback_data='achievement: ' + str(index) + ' ' + str(user_id))
            key.add(button)
        button = InlineKeyboardButton(text='Добавить достижение', callback_data='+achievement ' + str(user_id))
        key.add(button)
        bot.send_message(chat_id, 'Нажмите на достижение, чтобы удалить его, или нажмите на кнопку ДОБАВИТЬ, чтобы добавить новое', reply_markup=key)
    except Exception as err:
        print('Не удалось поменять достижения участника', err)
        bot.send_message(chat_id, 'Не удалось поменять достижения участника')


def edit_achievement(message, chat_id):
    try:
        number = int(message[message.find('achievement: ') + 13: message.rfind(' ')])
        user_id = str(message[message.rfind(' ') + 1: len(message)])
        user = backend.get_user(user_id)
        custom_achievements = []
        if 'custom_achievements' in user:
            custom_achievements = user['custom_achievements']
        del custom_achievements[number]
        backend.update_user(user_id, {'custom_achievements': custom_achievements})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось изменить достижения участника', err)
        bot.send_message(chat_id, 'Не удалось изменить достижения участника')


def add_achievement(message, chat_id):
    try:
        user_id = message[message.find(' ') + 1: len(message)]
        backend.insert_session(chat_id, 'achievement', {'user_id': user_id})
        bot.send_message(chat_id, 'Напишите достижение участника')
    except Exception as err:
        print('Не удалось добавить достижение участнику', err)
        bot.send_message(chat_id, 'Не удалось добавить достижение участнику')


def new_achievement(message, chat_id, args):
    try:
        backend.erase_session(chat_id)
        user_id = args['user_id']
        user = backend.get_user(user_id)
        custom_achievements = []
        if 'custom_achievements' in user:
            custom_achievements = user['custom_achievements']
        custom_achievements.append(message)
        backend.update_user(user_id, {'custom_achievements': custom_achievements})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось добавить новое достижение участнику', err)
        bot.send_message(chat_id, 'Не удалось добавить новое достижение участнику')