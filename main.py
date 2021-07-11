from threading import Thread
import telebot
import structure as struct
import index as req
import const
import admin
import texttable as table
import mongodb as backend
import re
import callback

import error
import keyboard
import text as text_creator

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

bot = const.bot
Thread1 = Thread(target=struct.take_contests)
Thread1.start()

def print_contests(chatId, prefix):
    try:
        key = InlineKeyboardMarkup()
        for contest in backend.get_contests():
            contestName = contest['name']
            id = contest['contest_id']
            button = InlineKeyboardButton(text=contestName, callback_data=prefix + 'id' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите контест:", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе контестов', err)


def print_users(chatId, prefix, admin):
    try:
        key = InlineKeyboardMarkup()
        if not admin:
            users = backend.get_users({'is_participant': not admin}).sort('is_participant')
        else:
            users = backend.get_users({}).sort('is_participant')
        for user in users:
            id = user['user_id']
            button = InlineKeyboardButton(text=user['active_name'], callback_data=prefix + 'login: ' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите пользователя:", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе пользователей', err)


def print_contest_information(chatId, contestId):
    try:
        contest = backend.get_contest_information(contestId)
        contestTop = contest['contestTop']
        rating = contest['allRating']
        top = ""
        if len(contestTop) >= 1:
            top += "Топ:\n" + "🥇 " + backend.get_user(contestTop[0][0])['name'] + " - " + str(contestTop[0][1]) \
                   + " " + struct.declension(contestTop[0][1], "задача", "задачи", "задач") + "\n"
        if len(contestTop) >= 2:
            top += "🥈 " + backend.get_user(contestTop[1][0])['name'] + " - " + str(contestTop[1][1]) \
                   + " " + struct.declension(contestTop[1][1], "задача", "задачи", "задач") + "\n"
        if len(contestTop) >= 3:
            top += "🥉 " + backend.get_user(contestTop[2][0])['name'] + " - " + str(contestTop[2][1]) \
                   + " " + struct.declension(contestTop[2][1], "задача", "задачи", "задач") + "\n"
        if len(contestTop) >= 1:
            top += "\n"

        first_submit = ""
        if 'firstSubmission' in contest:
            first_submit = "Первая успешная посылка:\n" + backend.get_user(contest['firstSubmission']['name'])['name'] + "\n"\
                           + "Время посылки: " + str(contest['firstSubmission']['time']) + " " + \
                           struct.declension(contest['firstSubmission']['time'], "минута", "минуты", "минут") + "\n\n"
        key = InlineKeyboardMarkup()
        but_1 = InlineKeyboardButton(text="Посмотреть активность",
                                     callback_data="not_admin_contest_id" + str(contestId))
        key.add(but_1)
        bot.send_message(chatId, "<b>" + contest['name'] + ":</b>\n\n" + first_submit + top +
                         "Рейтинг за тренировку:\n\n<pre>" + rating + "</pre>",
                         parse_mode="html", reply_markup=key)
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
        activity = ''
        for color in userInformation['last_activities']:
            activity += const.activity[color][0]
        bot.send_message(chatId, "<b>" + userInformation['active_name'] + ":</b>\n\n" +
                         "Div: " + str(userInformation['division']) + "\n" +
                         "Средняя активность:\n" + const.activity[userInformation['activity']] + "\nАктивность за 5 тренировок:\n" +
                        activity + '\n\n'
                         "Достижения:\n" + userInformation['achievements'] + "\n" + userAchievements + "\n" +
                         "Решено задач: " + str(userInformation['solved']) + "\n" +
                         "Не решено задач: " + str(userInformation['unsolved']) + "\n\n" +
                         "За последние 5 тренировок вы решили: \n" + str(userInformation['solvedLast']) + " " +
                         str(struct.declension(userInformation['solvedLast'], "задачу", "задачи", "задач")) + " из " +
                         str(userInformation['allLast']) + "\n",
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
    if message.chat.type == "private":
        print(str(message.chat.id) + ' ' + str(message.from_user.username) + ' ' + str(
            message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))  # логи

        backend.insert_user(message.from_user.id, alias=message.from_user.username)  # запоминаем пользователя в бд
        bot.send_message(message.chat.id, "Привет", reply_markup=keyboard.Menu())
        # bot.send_message(message.chat.id, "Выберите:", reply_markup=keyboard.InlineInfo())


@bot.message_handler(content_types=["text"])
def continue_chat(message):
    try:
        if message.chat.type == "private":
            userId = str(message.from_user.id)
            backend.insert_user(userId, alias=message.from_user.username)  # запоминаем пользователя в бд
            print(str(userId) + ' ' + str(message.from_user.username) + ' ' + str(
                message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))  # логи

            if backend.find_session(userId) is not None:  # проверка сессий
                session = backend.find_session(userId)
                backend.erase_session(userId)
                if message.text == '/cancel' and 'delete' in session['args']:
                    bot.delete_message(message.from_user.id, message.message_id)
                    bot.delete_message(chat_id=userId, message_id=session['args']['delete'])
                    return
                if session['name'] == 'achievement':
                    admin.new_achievement(message.text, userId, session['args'])
                elif session['name'] == 'change_contest_activity':
                    admin.change_activity(message.text, userId, session['args'])
                elif session['name'] == 'inline_profile_change_name':
                    bot.delete_message(message.from_user.id, message.message_id)
                    admin.edit_name(message.text, userId, session['args'])
                elif session['name'] == 'inline_profile_change_birthday':
                    bot.delete_message(message.from_user.id, message.message_id)
                    admin.edit_birthday(message.text, userId, session['args'])
                elif session['name'] == 'inline_profile_change_handleCF':
                    bot.delete_message(message.from_user.id, message.message_id)
                    admin.edit_handleCF(message.text, userId, session['args'])
                elif session['name'] == 'inline_profile_change_handleHQ':
                    bot.delete_message(message.from_user.id, message.message_id)
                    admin.edit_handleHQ(message.text, userId, session['args'])
                elif session['name'] == 'inline_profile_change_delete':
                    bot.delete_message(message.from_user.id, message.message_id)
                    admin.delete_user(message.text, userId, session['args'])
                elif session['name'] == 'inline_profile_change_confirmation':
                    bot.delete_message(message.from_user.id, message.message_id)
                    admin.confirm_user(message.text, userId, session['args'])
                elif session['name'] == 'inline_teams_change_name':
                    bot.delete_message(message.from_user.id, message.message_id)
                    admin.change_team_name(message.text, userId, session['args'])

            # elif message.text == "Меню":
            #     bot.send_message(userId, "Выберите:", reply_markup=keyboard.InlineInfo())
            elif message.text == "Профиль 👨‍💻":
                bot.send_message(userId, text_creator.SettingsInfo(userId, userId),
                                 reply_markup=keyboard.InlineProfile(userId, userId, profile=True), parse_mode='html')
            elif message.text == "Пользователи 👤":
                bot.send_message(userId, 'Выберите пользователя:',
                                 reply_markup=keyboard.InlineUsers(userId))
            elif message.text == "Команды 👥":
                bot.send_message(userId, 'Выберите команду:',
                                 reply_markup=keyboard.InlineTeams(userId))

            elif message.text.find('/all ') != -1 and admin.Check(userId):  # вывод сообщения всем пользователям
                for user in backend.get_users({}):
                    try:
                        bot.send_message(user['user_id'], message.text[message.text.find('/all ') + 5: len(message.text)])
                    except Exception as err:
                        print('Пользователь ' + user['user_id'] + ' удалил чат', err)

        elif message.chat.type == "supergroup":
            if message.text == "/rating@HQcontests_bot":
                print_all_rating(message.chat.id)
    except Exception as err:
        error.Log(errorAdminText='❗Произошла ошибка при обработке сообщения от пользователя ' + str(err),
                  userId=message.chat.id, errorUserText='Произошла ошибка')


@bot.callback_query_handler(func=lambda text: True)
def callback_text(text):
    chatId = text.from_user.id
    try:
        message = text.data
        print(str(text.message.chat.id) + ' ' + str(text.from_user.username) + ' ' + str(
            text.from_user.first_name) + ' ' + str(text.from_user.last_name) + ': ' + str(message))  # логи

        if backend.find_session(chatId) is not None:  # проверка сессий
            session = backend.find_session(chatId)
            backend.erase_session(chatId) # удаление сессии при нажатии на кнопку
            if message == '/cancel' and 'delete' in session['args']:
                bot.delete_message(message.from_user.id, message.message_id)
                bot.delete_message(chat_id=chatId, message_id=session['args']['delete'])
                return
            if session['name'] == 'inline_teams_settings_delete':
                admin.delete_team(message, chatId, session['args'])
            elif session['name'] == 'inline_profile_change_like':
                admin.like_profile(message, chatId, session['args'])

        if re.match('inline_profile_change_', message) is not None:  # настройки профиля
            callback.InlineProfile(text, re.split('inline_profile_change_', message, maxsplit=1)[1])
        elif re.match('inline_users_id', message) is not None:  # настройки профиля
            team = None
            if re.match('inline_users_id_team', message) is not None:
                id = re.split('inline_users_id_team', message, maxsplit=1)[1]
                userId = re.split('[+]', id, maxsplit=1)[0]
                team = re.split('[+]', id, maxsplit=1)[1]
            else:
                userId = re.split('inline_users_id', message, maxsplit=1)[1]
            bot.edit_message_text(chat_id=chatId, message_id=text.message.id, text=text_creator.SettingsInfo(userId, chatId),
                             reply_markup=keyboard.InlineProfile(userId, chatId, team), parse_mode='html')
        elif re.match('inline_teams_', message) is not None: # команды
            callback.InlineTeams(text, re.split('inline_teams_', message, maxsplit=1)[1])

        elif message == "getcontest":
            print_contests(chatId, '')
        elif message == "getuser":
            print_users(chatId, 'info', False)
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
        elif message.find('show_achievements ') != -1:
            admin.show_achievements(message, text.from_user.id)
        elif message.find('achievement: ') != -1:
            admin.edit_achievement(message, text.from_user.id)
        elif message.find('+achievement') != -1:
            admin.add_achievement(message, text.from_user.id)
        elif message.find('not_admin_contest_id') != -1:
            id = message[message.find('not_admin_contest_id') + 20: len(message)]
            admin.show_contest(id, text.message.chat.id, False)
        elif message.find('admin_contest_id') != -1:
            id = message[message.find('admin_contest_id') + 16: len(message)]
            admin.show_contest(id, text.message.chat.id, True)
        elif message.find('id') != -1:
            print_contest_information(text.message.chat.id, message[message.find('id') + 2: len(message)])
        elif message.find('admin_users') != -1:
            print_users(text.message.chat.id, 'admin_info_', True)  # вывод пользователей для админа
        elif message.find('admin_contests') != -1:
            print_contests(text.message.chat.id, 'admin_contest_')
        elif message.find('choose_div') != -1:
            contestId = message[message.find(' ') + 1 : message.rfind(' ')]
            chatId = message[message.rfind(' ') + 1: len(message)]
            admin.choose_div(contestId, chatId)
        elif message.find('div_') != -1:
            contestId = message[message.find(' ') + 1: message.rfind(' ')]
            chatId = message[message.rfind(' ') + 1: len(message)]
            div = message[message.find('_') + 1: message.find(' ')]
            admin.edit_activity(contestId, chatId, div)
    except Exception as err:
        print("Проблемы с callback", err)


bot.polling(none_stop=True)
