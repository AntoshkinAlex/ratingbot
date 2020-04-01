from threading import Thread
import telebot
import structure as struct
import index as req
import const
from operator import itemgetter
from telebot import types
from collections import OrderedDict
import texttable as table

TOKEN = "1108350056:AAGg7QZA6lABP8L3FPfYvTU4_WZJh5Rv9ck"
bot = telebot.TeleBot(TOKEN)

Thread1 = Thread(target=struct.take_contests)
Thread1.start()

def print_contests(chatId):
    key = types.InlineKeyboardMarkup()
    for i in const.hq_contests:
        contestName = req.get_contestName(i)
        button = types.InlineKeyboardButton(text=contestName, callback_data='id' + str(i))
        key.add(button)
    bot.send_message(chatId, "Выберите контест:", reply_markup=key)


"""table = texttable.Texttable()
table.set_cols_align(["c", "c", "c"])
table.set_cols_valign(["m", "m", "m"])
table.set_deco(texttable.Texttable.HEADER)#, texttable.Texttable.HEADER)
table.add_rows([["Name", "Age", "Nickname"],
                ["Mr\nXavier\nHuon", 32, "Xav'"],
                ["Mr\nBaptiste\nClement", 1, "Baby"],
                ["Mme\nLouise\nBourgeau", 28, "Lou\nLoue"]])
print(table.draw() + "\n")
table = texttable.Texttable()
table.set_deco(texttable.Texttable.HEADER)#, texttable.Texttable.HEADER)
table.set_cols_dtype(['t',  # text
                      'f',  # float (decimal)
                      'e',  # float (exponent)
                      'i',  # integer
                      'a']) # automatic
table.set_cols_align(["l", "r", "r", "r", "l"])
table.add_rows([["text",    "float", "exp", "int", "auto"],
                ["abcd",    "67",    654,   89,    128.001],
                ["efghijk", 67.5434, .654,  89.6,  12800000000000000000000.00023],
                ["lmn",     5e-78,   5e-78, 89.4,  .000000000000128],
                ["opqrstu", .023,    5e+78, 92.,   12800000000000000000000]])
"""

def print_contest_information(chatId, contestId):
    contest = struct.get_contest_information(contestId)
    contestTop = struct.get_first_three_place(contestId)
    #rating = ""
    sortedRating = []
    for user in contest['users']:
        sortedRating.append([contest['users'][user]['rating'], user])
    sortedRating.sort()
    sortedRating.reverse()

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


def print_all_rating(chatId):
    rating = struct.get_all_rating()
    print_rating = table.Texttable()
    print_rating.set_deco(table.Texttable.HEADER)
    print_rating.set_cols_align(["l", "c", "c"])
    print_rating.set_cols_valign(["t", "t", "m"])
    print_rating.set_cols_dtype(['t', 'i', 'i'])
    print_rating.add_row(["Фамилия\n", "🏆\n", "Задачи\n"])
    space = '  '
    for index, user in enumerate(rating):
        userName = str(const.handles[user])
        name = userName[userName.find(' ') + 1 : ]
        if (index == 9):
            space = ' '
        print_rating.add_row([str(index + 1) + space +
                              name,
                              str(rating[user]['rating']),
                              str(rating[user]['solved'] + rating[user]['upsolved'])
                              ])
    bot.send_message(chatId, "<b>" + "Общий рейтинг:" + "</b>\n\n<pre>" + print_rating.draw() + "</pre>", parse_mode="html")


@bot.message_handler(commands=["start"])
def start_chat(message):
    menuKey = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menuBut = types.KeyboardButton(text = "Меню")
    menuKey.add(menuBut)

    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
    but_2 = types.InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
    key.add(but_1, but_2)

    bot.send_message(message.chat.id, "Привет", reply_markup=menuKey)
    bot.send_message(message.chat.id, "Выберите:", reply_markup=key)

@bot.message_handler(content_types=["text"])
def continue_chat(message):
    print(str(message.from_user.username) + ' ' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))
    if (message.text == "Меню"):
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
        but_2 = types.InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
        key.add(but_1, but_2)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=key)

@bot.callback_query_handler(func=lambda text:True)
def callback_text(text):
    message = text.data
    print(str(text.from_user.username) + ' ' + str(text.from_user.first_name) + ' ' + str(text.from_user.last_name)+ ': ' + str(message))
    if message == "getcontest":
        print_contests(text.message.chat.id)
    elif message == "getrating":
        print_all_rating(text.message.chat.id)
    elif message.find('id') != -1:
        print_contest_information(text.message.chat.id, message[message.find('id') + 2 : len(message)])



bot.polling(none_stop = True)