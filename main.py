from threading import Thread
import telebot
import structure as struct
import index as req
import const
from telebot import types
import texttable as table

bot = const.bot
Thread1 = Thread(target=struct.take_contests)
Thread1.start()


def print_contests(chatId):
    try:
        key = types.InlineKeyboardMarkup()
        for i in const.hq_contests:
            contestName = const.name_id_contests[i]
            id = i
            button = types.InlineKeyboardButton(text=contestName, callback_data='id' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите контест:", reply_markup=key)
    except:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка')

def print_users(chatId):
    try:
        key = types.InlineKeyboardMarkup()
        for i in const.handles:
            userInformation = const.user_information[i]
            id = i
            button = types.InlineKeyboardButton(text=userInformation['name'], callback_data='login: ' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите пользователя:", reply_markup=key)
    except:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка')


def print_contest_information(chatId, contestId):
    try:
        contest = const.hq_contest_information[contestId]['contest']
        contestTop = const.hq_contest_information[contestId]['contestTop']
        sortedRating = const.hq_contest_information[contestId]['sortedRating']

        rating = table.Texttable()
        rating.set_deco(table.Texttable.HEADER)
        rating.set_cols_align(["l", "c"])
        rating.set_cols_valign(["t", "t"])
        rating.set_cols_dtype(['t', 't'])
        rating.add_row(["Фамилия\n", "🏆\n"])
        space = '  '
        for index, item in enumerate(sortedRating):
            userName = const.handles[item[1]]
            name = userName[userName.find(' ') + 1 : ]
            if (index == 9):
                space = ' '
            rating.add_row([str(index + 1) + space +
                                  str(name),
                                  str(contest['users'][item[1]]['rating']) +
                                  " (" + str(contest['users'][item[1]]['solvedCount']) + "/" + str(contest['users'][item[1]]['upsolvedCount']) + ")"
                                  ])
    except Exception as err:
        print(err)
        print('Ошибка при выводе информации о контесте')

    try:
        bot.send_message(chatId, "<b>" + contest['name'] + ":</b>\n\n" +
                         "Первая успешная посылка:\n" + const.handles[contest['firstSubmission']['name']] + "\n" +
                         "Время посылки: " + str(contest['firstSubmission']['time']) + " " + struct.declension(
            contest['firstSubmission']['time'], "минута", "минуты", "минут") + "\n\n" +
                         "Топ:\n" +
                         "🥇 " + const.handles[contestTop[0][0]] + " - " + str(contestTop[0][1]) + " " +
                         struct.declension(contestTop[0][1], "задача", "задачи", "задач") + "\n" +
                         "🥈 " + const.handles[contestTop[1][0]] + " - " + str(contestTop[1][1]) + " " +
                         struct.declension(contestTop[1][1], "задача", "задачи", "задач") + "\n" +
                         "🥉 " + const.handles[contestTop[2][0]] + " - " + str(contestTop[2][1]) + " " +
                         struct.declension(contestTop[2][1], "задача", "задачи", "задач") + "\n\n" +
                         "Рейтинг за тренировку:\n\n<pre>" + rating.draw() + "</pre>",
                         parse_mode="html")
    except:
        bot.send_message(chatId, "Произошла ошибка")


def print_user_information(chatId, user):
    try:
        userInformation = const.user_information[user]
        bot.send_message(chatId, "<b>" + userInformation['name'] + ":</b>\n\n" +
                "Активность:\n" + userInformation['activity'] + "\n\n" +
                "Достижения:\n" + userInformation['achievements'] + "\n\n" +
                "Решено задач: " + str(userInformation['solved']) + "\n" +
                "Не решено задач: " + str(userInformation['unsolved']) + "\n\n" +
                "За последние 5 тренировок вы решили: \n" + str(userInformation['solvedLast']) + " " +
                 str(struct.declension(userInformation['solvedLast'], "задачу", "задачи", "задач")) + " из " +
                         str(userInformation['allLast']) + "\n",
                parse_mode="html")
    except:
        print('Ошибка при выводе личной информации')
        bot.send_message(chatId, "Произошла ошибка")


def print_all_rating(chatId):
    try:
        bot.send_message(chatId, "<b>" + "Общий рейтинг:" + "</b>\n\n<pre>" + const.all_rating.draw() + "</pre>", parse_mode="html")
    except:
        bot.send_message(chatId, 'Произошла ошибка')


@bot.message_handler(commands=["start"])
def start_chat(message):
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
    print(str(message.chat.id) + ' ' + str(message.from_user.username) + ' ' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))
    if (message.text == "Меню"):
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
                bot.send_message(user, message.text[message.text.find('/user ') + 7 + len(const.users[user]) : len(message.text)])
                bot.send_message('374683082', 'Доставлено')


@bot.callback_query_handler(func=lambda text:True)
def callback_text(text):
    message = text.data
    print(str(text.message.chat.id) + ' ' + str(text.from_user.username) + ' ' + str(text.from_user.first_name) + ' ' + str(text.from_user.last_name)+ ': ' + str(message))
    if message == "getcontest":
        print_contests(text.message.chat.id)
    elif message == "getrating":
        print_all_rating(text.message.chat.id)
    elif message == "getuser":
        print_users(text.message.chat.id)
    elif message.find('login: ') != -1:
        print_user_information(text.message.chat.id, message[message.find('login: ') + 7: len(message)])
    elif message.find('id') != -1:
        print_contest_information(text.message.chat.id, message[message.find('id') + 2 : len(message)])



bot.polling(none_stop = True)