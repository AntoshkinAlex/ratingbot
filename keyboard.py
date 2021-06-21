from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import admin
import mongodb as backend
import error

def Menu():
    menuKey = ReplyKeyboardMarkup(resize_keyboard=True)
    menuBut = KeyboardButton(text="Меню")
    profileBut = KeyboardButton(text="Профиль 👨‍💻")
    usersBut = KeyboardButton(text="Пользователи 👥")
    menuKey.add(menuBut, usersBut)
    menuKey.add(profileBut)
    return menuKey


def InlineInfo():
    keyboard = InlineKeyboardMarkup()
    trainingBut = InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
    infoBut = InlineKeyboardButton(text="Личная информация", callback_data="getuser")
    keyboard.add(trainingBut, infoBut)
    return keyboard


def InlineProfile(userId, chatId):
    userId = str(userId)  # id пользователя
    chatId = str(chatId)
    is_admin = admin.Check(chatId)
    keyboard = InlineKeyboardMarkup()  # клавиатура с изменением настроек пользователя
    nameBut = InlineKeyboardButton(text="Фамилия Имя", callback_data="inline_profile_change_name_id" + userId)
    birthdayBut = InlineKeyboardButton(text="Дата рождения",
                                       callback_data="inline_profile_change_birthday_id" + userId)
    handleCFBut = InlineKeyboardButton(text="Хэндл Codeforces",
                                     callback_data="inline_profile_change_handleCF_id" + userId)
    notificationsBut = InlineKeyboardButton(text="Вкл/выкл уведомления",
                                            callback_data="inline_profile_change_notifications_id" + userId)
    if is_admin or userId == chatId:
        keyboard.add(nameBut)
        keyboard.add(birthdayBut)
        keyboard.add(handleCFBut)
        keyboard.add(notificationsBut)
    if is_admin:
        handleHQBut = InlineKeyboardButton(text="Хэндл HQ Contests", callback_data="inline_profile_change_handleHQ_id" + userId)
        participantBut = InlineKeyboardButton(text="Является участником HQ", callback_data="inline_profile_change_is_participant_id" + userId)
        confirmationBut = InlineKeyboardButton(text="Подтвердить профиль ✅", callback_data="inline_profile_change_confirmation_id" + userId)
        keyboard.add(handleHQBut)
        keyboard.add(participantBut)
        keyboard.add(confirmationBut)
        if admin.MainAdmin(chatId):
            adminBut = InlineKeyboardButton(text="Вкл/выкл администрирование ", callback_data="inline_profile_change_admin_id" + userId)
            keyboard.add(adminBut)
            deleteBut = InlineKeyboardButton(text="Удалить пользователя ❌", callback_data="inline_profile_change_delete_id" + userId)
            keyboard.add(deleteBut)
    return keyboard


def InlineUsers(chatId):
    try:
        chatId = str(chatId)
        is_admin = admin.Check(chatId)
        keyboard = InlineKeyboardMarkup()  # клавиатура с пользователями
        params = {}
        if not is_admin:
            params = {'is_participant': True}
        backend_users = backend.get_users(params)
        good_users = []
        for user in backend_users:
            user_name = user['name'][: user['name'].find(' ')]
            new_user = [user_name, user['user_id']]
            if 'confirmation' in user and user['confirmation'] != {} and is_admin:
                new_user.append(True)
            else:
                new_user.append(False)
            good_users.append(new_user)
        good_users.sort()
        if len(good_users) % 2:
            good_users.append([' ', 'None'])
        line_count = len(good_users) // 2
        for i in range(line_count):
            def checkConfirmation(confirm):
                if is_admin and confirm:
                    return ' ⚠️'
                else:
                    return ''
            user = good_users[i]
            leftBut = InlineKeyboardButton(text=user[0] + checkConfirmation(user[2]),
                                           callback_data="inline_users_id" + user[1])
            user = good_users[line_count + i]
            if user[1] == 'None':
                rightBut = InlineKeyboardButton(text=user[0], callback_data='Null')
            else:
                rightBut = InlineKeyboardButton(text=user[0] + checkConfirmation(user[2]),
                                                callback_data="inline_users_id" + user[1])
            keyboard.add(leftBut, rightBut)
        return keyboard
    except Exception as err:
        error.Log(errorAdminText='❗Произошла ошибка при создании клавиатуры с пользователями' + str(err))
