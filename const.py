import texttable as table
import telebot

TOKEN = "1108350056:AAGg7QZA6lABP8L3FPfYvTU4_WZJh5Rv9ck"
bot = telebot.TeleBot(TOKEN)
apiKey = ["ea22ef6a8048cfcd258e9242151cb1141bf16c23", "147ec3d78a8170c07def4d0b7032afcfae0f3292"]
apiSecret = ["1435eb83678671d1c94ef43e9ded1e5e719501ba", "b8b59bae8bda9bec15c02f76f65491c4c2de89da"]
authors = ['antoshkin', 'aafonin']
hq_contests = []
apis = {}
name_id_contests = {}
hq_rating_information = {}
all_rating = table.Texttable()
name_contests = {}
hq_contest_information = {}
user_information = {}
goodluck = []
reminder = []

handles = {
    'afonkin-hq': 'Павел Афонькин',
    'bazilov-hq': 'Дмитрий Базилов',
    'vasil-hq': 'Сергей Василянский',
    'galuza-hq': 'Владислав Галуза',
    'guryanov-hq': 'Максим Гурьянов',
    'movzalevskaya-hq': 'Виталия Мовзалевская',
    'movsesyan-hq': 'Владимир Мовсесян',
    'povol-hq': 'Роман Поволоцкий',
    'pugachev-hq': 'Дмитрий Пугачёв',
    'seleznev-hq': 'Виктор Селезнёв',
    'solov-hq': 'Полина Соловьёва',
    'tutichkin-hq': 'Семён Тютичкин',
    'filatov-hq': 'Юрий Филатов',
    'khadzakos-hq': 'Николай Хадзакос',
    'shevnin-hq': 'Даниил Шевнин',
}

admins = [
    '374683082',
    '836229942'
]

users = {
    '797286916': 'Павел Афонькин',
    # 'bazilov-hq': 'Дмитрий Базилов',
    '976786169': 'Сергей Василянский',
    # '----': 'Владислав Галуза',
    '758268123': 'Максим Гурьянов',
    '941135020': 'Виталия Мовзалевская',
    '407260042': 'Владимир Мовсесян',
    '727246784': 'Роман Поволоцкий',
    '409643555': 'Дмитрий Пугачёв',
    # 'seleznev-hq': 'Виктор Селезнёв',
    '429844258': 'Полина Соловьёва',
    '320398520': 'Семён Тютичкин',
    '600118091': 'Юрий Филатов',
    '379999478': 'Николай Хадзакос',
    '1011350398': 'Даниил Шевнин',
    '374683082': 'Алексей Антошкин',
    '836229942': 'Александр Афонин',
}

first_course = {
    'vasil-hq': 'Сергей Василянский',
    'galuza-hq': 'Владислав Галуза',
    'guryanov-hq': 'Максим Гурьянов',
    'filatov-hq': 'Юрий Филатов',
    'pugachev-hq': 'Дмитрий Пугачёв',
    'khadzakos-hq': 'Николай Хадзакос',
    'shevnin-hq': 'Даниил Шевнин',
}
