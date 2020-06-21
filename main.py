from threading import Thread
import telebot
import structure as struct
import index as req
import const
import admin
from telebot import types
import texttable as table
import mongodb as backend

bot = const.bot
Thread1 = Thread(target=struct.take_contests)
Thread1.start()


def print_contests(chatId):
    try:
        key = types.InlineKeyboardMarkup()
        for contest in backend.get_contests():
            contestName = contest['name']
            id = contest['contest_id']
            button = types.InlineKeyboardButton(text=contestName, callback_data='id' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите контест:", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе контестов', err)


def print_users(chatId, prefix, admin):
    try:
        key = types.InlineKeyboardMarkup()
        for user in backend.get_users(not(admin)).sort('is_participant'):
            backend.insert_user(user['user_id'])
            id = user['user_id']
            button = types.InlineKeyboardButton(text=user['active_name'], callback_data=prefix + 'login: ' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите пользователя:", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе пользователей', err)


def print_contest_information(chatId, contestId):
    try:
        hq_contest_information = backend.get_contest_information(contestId)
        contest = hq_contest_information
        contestTop = hq_contest_information['contestTop']
        sortedRating = hq_contest_information['sortedRating']
        rating = table.Texttable()
        rating.set_deco(table.Texttable.HEADER)
        rating.set_cols_align(["l", "c"])
        rating.set_cols_valign(["t", "t"])
        rating.set_cols_dtype(['t', 't'])
        rating.add_row(["Фамилия\n", "🏆\n"])
        space = '  '
        for index, item in enumerate(sortedRating):
            userName = backend.get_user(item[1])['name']
            name = userName[userName.find(' ') + 1 : ]
            if (index == 9):
                space = ' '
            rating.add_row([str(index + 1) + space +
                                  str(name),
                                  str(contest['users'][item[1]]['rating']) +
                                  " (" + str(contest['users'][item[1]]['solvedCount']) + "/" + str(contest['users'][item[1]]['upsolvedCount']) + ")"
                                  ])
    except Exception as err:
        print('Ошибка при выводе информации о контесте', err)

    try:
        bot.send_message(chatId, "<b>" + contest['name'] + ":</b>\n\n" +
                         "Первая успешная посылка:\n" + backend.get_user(contest['firstSubmission']['name'])['name'] + "\n" +
                         "Время посылки: " + str(contest['firstSubmission']['time']) + " " + struct.declension(
            contest['firstSubmission']['time'], "минута", "минуты", "минут") + "\n\n" +
                         "Топ:\n" +
                         "🥇 " + backend.get_user(contestTop[0][0])['name'] + " - " + str(contestTop[0][1]) + " " +
                         struct.declension(contestTop[0][1], "задача", "задачи", "задач") + "\n" +
                         "🥈 " + backend.get_user(contestTop[1][0])['name'] + " - " + str(contestTop[1][1]) + " " +
                         struct.declension(contestTop[1][1], "задача", "задачи", "задач") + "\n" +
                         "🥉 " + backend.get_user(contestTop[2][0])['name'] + " - " + str(contestTop[2][1]) + " " +
                         struct.declension(contestTop[2][1], "задача", "задачи", "задач") + "\n\n" +
                         "Рейтинг за тренировку:\n\n<pre>" + rating.draw() + "</pre>",
                         parse_mode="html")
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка при выводе таблицы контеста", err)


def print_user_information(chatId, user):
    try:
        userInformation = backend.get_user(user)
        userAchievements = '\n'
        if 'custom_achievements' in userInformation:
            userAchievements = ''
            for achievement in userInformation['custom_achievements']:
                userAchievements += str(achievement) + '\n'
        bot.send_message(chatId, "<b>" + userInformation['active_name'] + ":</b>\n\n" +
                "Div: " + str(userInformation['division']) + "\n" +
                "Активность:\n" + userInformation['activity'] + "\n\n" +
                "Достижения:\n" + userInformation['achievements'] + "\n" + userAchievements + "\n\n" +
                "Решено задач: " + str(userInformation['solved']) + "\n" +
                "Не решено задач: " + str(userInformation['unsolved']) + "\n\n" +
                "За последние 5 тренировок вы решили: \n" + str(userInformation['solvedLast']) + " " +
                 str(struct.declension(userInformation['solvedLast'], "задачу", "задачи", "задач")) + " из " +
                    str(userInformation['allLast']) + "\n" +
                "Ваша активность составляет: " + str(userInformation['percent']) + "%\n",
                parse_mode="html")
    except Exception as err:
        print('Ошибка при выводе личной информации', err)
        bot.send_message(chatId, "Произошла ошибка")



def print_all_rating(chatId):
    rating = backend.get_rating()
    rating = rating['rating']
    try:
        bot.send_message(chatId, "<b>" + "Общий рейтинг:" + "</b>\n\n<pre>" + rating + "</pre>", parse_mode="html")
    except Exception as err:
        bot.send_message(chatId, 'Произошла ошибка при выводе общего рейтинга', err)


@bot.message_handler(commands=["start"])
def start_chat(message):
    backend.insert_user(message.from_user.id)
    backend.erase_session(message.from_user.id)
    menuKey = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menuBut = types.KeyboardButton(text="Меню")
    menuKey.add(menuBut)

    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
    but_2 = types.InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
    but_3 = types.InlineKeyboardButton(text="Личная информация", callback_data="getuser")
    key.add(but_1, but_2)
    key.add(but_3)

    bot.send_message(message.chat.id, "Привет", reply_markup=menuKey)
    bot.send_message(message.chat.id, "Выберите:", reply_markup=key)


@bot.message_handler(content_types=["text"])
def continue_chat(message):
    backend.insert_user(message.from_user.id)
    print(str(message.chat.id) + ' ' + str(message.from_user.username) + ' ' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))
    if backend.find_session(message.from_user.id) is not None:
        session = backend.find_session(message.from_user.id)
        backend.erase_session(message.from_user.id)
        if session['name'] == 'achievement':
            admin.new_achievement(message.text, message.from_user.id, session['args'])
    elif message.text == "Меню":
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
        but_2 = types.InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
        but_3 = types.InlineKeyboardButton(text="Личная информация", callback_data="getuser")
        key.add(but_1, but_2)
        key.add(but_3)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=key)
    elif message.text.find('/all ') != -1 and str(message.chat.id) in const.admins:
        for user in const.users:
            bot.send_message(user, message.text[message.text.find('/all ') + 5 : len(message.text)])
    elif message.text.find('/user ') != -1 and str(message.chat.id) in const.admins:
        for user in const.users:
            if message.text.find(const.users[user]) != -1:
                mes = message.text[message.text.find('/user ') + 7 + len(const.users[user]) : len(message.text)]
                bot.send_message(user, mes)
                bot.send_message(str(message.chat.id), 'Бот Саша успешно доставил сообщение:\n' + mes)
    elif message.text.find('/admin') != -1:
        if str(message.chat.id) in const.admins:
            print_users(message.chat.id, 'admin_info_', True)
        else:
            img = open('Who_are_u?.jpg', 'rb')
            bot.send_photo(message.chat.id, img)


@bot.callback_query_handler(func=lambda text:True)
def callback_text(text):
    backend.erase_session(text.from_user.id)
    try:
        message = text.data
        backend.insert_user(text.from_user.id)
        print(str(text.message.chat.id) + ' ' + str(text.from_user.username) + ' ' + str(text.from_user.first_name) + ' ' + str(text.from_user.last_name)+ ': ' + str(message))
        if message == "getcontest":
            print_contests(text.message.chat.id)
        elif message == "getrating":
            print_all_rating(text.message.chat.id)
        elif message == "getuser":
            print_users(text.message.chat.id, 'info', False)
        elif message.find('infologin: ') != -1:
            print_user_information(text.message.chat.id, message[message.find('infologin: ') + 11: len(message)])
        elif message.find('admin_info_login: ') != -1:
            try:
                user_id = message[message.find('admin_info_login: ') + 18: len(message)]
                admin.print_admin_user_information(text.message.chat.id, user_id)
            except Exception as err:
                print('Не удалось вывести пользователя админу', err)
                bot.send_message(text.message.chat.id, 'Не удалось вывести пользователя')
        elif message.find('change_div ') != -1:
            admin.change_div(message, text.from_user.id)
        elif message.find('change_participant ') != -1:
            admin.change_participant(message, text.from_user.id)
        elif message.find('show_achievements ') != -1:
            admin.show_achievements(message, text.from_user.id)
        elif message.find('achievement: ') != -1:
            admin.edit_achievement(message, text.from_user.id)
        elif message.find('+achievement') != -1:
            admin.add_achievement(message, text.from_user.id)
        elif message.find('id') != -1:
            print_contest_information(text.message.chat.id, message[message.find('id') + 2: len(message)])
    except Exception as err:
        print("Проблемы с callback", err)



bot.polling(none_stop = True)