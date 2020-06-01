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
    'vasil-hq': 'Сергей Василянский',
    'galuza-hq': 'Владислав Галуза',
    'guryanov-hq': 'Максим Гурьянов',
    'zhuravlev-hq': 'Виктор Журавлёв',
    'movzalevskaya-hq': 'Виталия Мовзалевская',
    'movsesyan-hq': 'Владимир Мовсесян',
    'nazarov-hq': 'Аркадий Назаров',
    'povol-hq': 'Роман Поволоцкий',
    'pugachev-hq': 'Дмитрий Пугачёв',
    'seleznev-hq': 'Виктор Селезнёв',
    'solov-hq': 'Полина Соловьёва',
    'tutichkin-hq': 'Семён Тютичкин',
    'filatov-hq': 'Юрий Филатов',
    'khadzakos-hq': 'Николай Хадзакос'
}

admins = [
    '374683082',
    '836229942'
]

users = {
    '797286916': 'Афонькин',
    '976786169': 'Василянский',
    '783199820': 'Галуза',
    '758268123': 'Гурьянов',
    '787009991': 'Журавлёв',
    '941135020': 'Мовзалевская',
    '407260042': 'Мовсесян',
    '727246784': 'Поволоцкий',
    '409643555': 'Пугачёв',
    '522998780': 'Селезнёв',
    '429844258': 'Соловьёва',
    '320398520': 'Тютичкин',
    '600118091': 'Филатов',
    '379999478': 'Хадзакос',
    '1224120254': 'Назаров',
    '374683082': 'Антошкин',
    '836229942': 'Афонин'
}

first_course = {
    'vasil-hq': 'Сергей Василянский',
    'galuza-hq': 'Владислав Галуза',
    'guryanov-hq': 'Максим Гурьянов',
    'filatov-hq': 'Юрий Филатов',
    'pugachev-hq': 'Дмитрий Пугачёв',
    'nazarov-hq': 'Аркадий Назаров',
    'khadzakos-hq': 'Николай Хадзакос'
}

userAchievements = {
    'afonkin-hq': '',
    'vasil-hq': '',
    'galuza-hq': '',
    'guryanov-hq': '',
    'zhuravlev-hq': '🎖 - Победил в кахуте',
    'movzalevskaya-hq': '',
    'movsesyan-hq': '',
    'nazarov-hq': '',
    'povol-hq': '',
    'pugachev-hq': '',
    'seleznev-hq': '',
    'solov-hq': '',
    'tutichkin-hq': '',
    'filatov-hq': '',
    'khadzakos-hq': ''
}
