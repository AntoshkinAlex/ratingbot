import texttable as table
import telebot

TOKEN = "1108350056:AAGg7QZA6lABP8L3FPfYvTU4_WZJh5Rv9ck"
bot = telebot.TeleBot(TOKEN)
apiKey = ["ea22ef6a8048cfcd258e9242151cb1141bf16c23", "147ec3d78a8170c07def4d0b7032afcfae0f3292"]
apiSecret = ["1435eb83678671d1c94ef43e9ded1e5e719501ba", "b8b59bae8bda9bec15c02f76f65491c4c2de89da"]
MONGODB_LINK = "mongodb+srv://Alexey:a2622326@hqbot.xabdv.mongodb.net/HQbot?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
MONGODB = "HQbot"

authors = ['antoshkin', 'aafonin']
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
    'khadzakos-hq': 'Николай Хадзакос',
}

users_id = {
    '797286916': 'afonkin-hq',
    '976786169': 'vasil-hq',
    '783199820': 'galuza-hq',
    '758268123': 'guryanov-hq',
    '787009991': 'zhuravlev-hq',
    '941135020': 'movzalevskaya-hq',
    '407260042': 'movsesyan-hq',
    '1224120254': 'nazarov-hq',
    '727246784': 'povol-hq',
    '409643555': 'pugachev-hq',
    '522998780': 'seleznev-hq',
    '429844258': 'solov-hq',
    '320398520': 'tutichkin-hq',
    '600118091': 'filatov-hq',
    '379999478': 'khadzakos-hq',
}

users_handles = {
    'afonkin-hq': '797286916',
    'vasil-hq': '976786169',
    'galuza-hq': '783199820',
    'guryanov-hq': '758268123',
    'zhuravlev-hq': '787009991',
    'movzalevskaya-hq': '941135020',
    'movsesyan-hq': '407260042',
    'nazarov-hq': '1224120254',
    'povol-hq': '727246784',
    'pugachev-hq': '409643555',
    'seleznev-hq': '522998780',
    'solov-hq': '429844258',
    'tutichkin-hq': '320398520',
    'filatov-hq': '600118091',
    'khadzakos-hq': '379999478',
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
