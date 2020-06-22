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
    global users
    try:
        key = types.InlineKeyboardMarkup()
        if not admin:
            users = backend.get_users({'is_participant': not admin}).sort('is_participant')
        else:
            backend.get_users({}).sort('is_participant')
        for user in users:
            id = user['user_id']
            button = types.InlineKeyboardButton(text=user['active_name'], callback_data=prefix + 'login: ' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите пользователя:", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе пользователей', err)


def print_settings(chatId):
    try:
        key = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Вкл/Выкл уведомления', callback_data='notifications')
        key.add(button)
        user = backend.get_user(chatId)
        notifications = user['notifications']
        status = 'Уведомления: '
        if notifications:
            status += '🟢'
        else:
            status += '🔴'
        bot.send_message(chatId, status, reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе настроек пользователя', err)


def print_contest_information(chatId, contestId):
    try:
        contest = backend.get_contest_information(contestId)
        contestTop = contest['contestTop']
        sortedRating = contest['sortedRating']
        rating = table.Texttable()
        rating.set_deco(table.Texttable.HEADER)
        rating.set_cols_align(["l", "c"])
        rating.set_cols_valign(["t", "t"])
        rating.set_cols_dtype(['t', 't'])
        rating.add_row(["Фамилия\n", "🏆\n"])
        space = '  '
        for index, item in enumerate(sortedRating):
            userName = backend.get_user(item[1])['name']
            name = userName[userName.find(' ') + 1:]
            if index == 9:
                space = ' '
            rating.add_row([str(index + 1) + space +
                            str(name),
                            str(contest['users'][item[1]]['rating']) +
                            " (" + str(contest['users'][item[1]]['solvedCount']) + "/" + str(
                                contest['users'][item[1]]['upsolvedCount']) + ")"
                            ])
    except Exception as err:
        print('Ошибка при выводе информации о контесте', err)

    try:
        bot.send_message(chatId, "<b>" + contest['name'] + ":</b>\n\n" +
                         "Первая успешная посылка:\n" + backend.get_user(contest['firstSubmission']['name'])[
                             'name'] + "\n" +
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
    backend.insert_user(message.from_user.id)  # запоминаем пользователя в бд

    menuKey = types.ReplyKeyboardMarkup(resize_keyboard=True)  # кнопка меню
    menuBut = types.KeyboardButton(text="Меню")
    menuKey.add(menuBut)

    key = types.InlineKeyboardMarkup() # кнопки взаимодействия
    but_1 = types.InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
    but_2 = types.InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
    but_3 = types.InlineKeyboardButton(text="Личная информация", callback_data="getuser")
    key.add(but_1, but_2)
    key.add(but_3)

    bot.send_message(message.chat.id, "Привет", reply_markup=menuKey)
    bot.send_message(message.chat.id, "Выберите:", reply_markup=key)


@bot.message_handler(content_types=["text"])
def continue_chat(message):
    backend.insert_user(message.from_user.id)  # запоминаем пользователя в бд

    print(str(message.chat.id) + ' ' + str(message.from_user.username) + ' ' + str(
        message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))  # логи

    if backend.find_session(message.from_user.id) is not None:  # проверка сессий
        session = backend.find_session(message.from_user.id)
        backend.erase_session(message.from_user.id)
        if session['name'] == 'achievement':
            admin.new_achievement(message.text, message.from_user.id, session['args'])
    elif message.text == "Меню":
        key = types.InlineKeyboardMarkup()  # кнопки взаимодействия
        but_1 = types.InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
        but_2 = types.InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
        but_3 = types.InlineKeyboardButton(text="Личная информация", callback_data="getuser")
        key.add(but_1, but_2)
        key.add(but_3)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=key)
    elif message.text.find('/all ') != -1 and str(message.chat.id) in const.admins:  # вывод сообщения всем пользователям
        for user in const.users:
            bot.send_message(user, message.text[message.text.find('/all ') + 5: len(message.text)])
    elif message.text.find('/admin') != -1:  # вывод пользователей для админа
        if str(message.chat.id) in const.admins:
            print_users(message.chat.id, 'admin_info_', True)
        else:
            img = open('Who_are_u?.jpg', 'rb')
            bot.send_photo(message.chat.id, img)
    elif message.text.find('/settings') != -1: # настройки
        print_settings(message.chat.id)


@bot.callback_query_handler(func=lambda text: True)
def callback_text(text):
    backend.erase_session(text.from_user.id)  # удаление сессии при нажатии на кнопку
    try:
        message = text.data
        print(str(text.message.chat.id) + ' ' + str(text.from_user.username) + ' ' + str(
            text.from_user.first_name) + ' ' + str(text.from_user.last_name) + ': ' + str(message))  # логи
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
        elif message.find('notifications') != -1:
            user = backend.get_user(text.message.chat.id)
            new_notifications = not user['notifications']
            backend.update_user(text.message.chat.id, {'notifications': new_notifications})
            print_settings(text.message.chat.id)
    except Exception as err:
        print("Проблемы с callback", err)


bot.polling(none_stop=True)
