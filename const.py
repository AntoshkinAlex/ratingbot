import telebot

TOKEN = "1211770497:AAF209K-usTLjMvdPBVzjmJbe1CxRvqUig4"
WEATHER_API = "8bb2a2b72751f9fd9f5e87183c354f2e"
bot = telebot.TeleBot(TOKEN)
apiKey = ["ea22ef6a8048cfcd258e9242151cb1141bf16c23", "147ec3d78a8170c07def4d0b7032afcfae0f3292", '1f52df94548e5e21e2df7ec4caf756cc516117ec']
apiSecret = ["1435eb83678671d1c94ef43e9ded1e5e719501ba", "b8b59bae8bda9bec15c02f76f65491c4c2de89da", '08018349bce0440f51f875dc9d0c0e78d8ea1a64']
MONGODB_LINK = "mongodb+srv://Alexey:a2622326@hqbot.xabdv.mongodb.net/HQbot?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
MONGODB = "HQbot"

authors = ['antoshkin', 'aafonin', 'pavel-afonkin']

activity = [
    '🔴 Очень низкий уровень активности',
    '🟠 Низкий уровень активности',
    '🟡 Средний уровень активности',
    '🟢 Высокий уровень активности',
    '🟣 Очень высокий уровень активности'
]

mainAdmin = '374683082№'
