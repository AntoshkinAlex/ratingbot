from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import admin
import mongodb as backend
import error

def Menu():
    menuKey = ReplyKeyboardMarkup(resize_keyboard=True)
    menuBut = KeyboardButton(text="Меню")
    profileBut = KeyboardButton(text="Профиль 👨‍💻")
    usersBut = KeyboardButton(text="Пользователи 👤")
    teamBut = KeyboardButton(text="Команды 👥")
    menuKey.add(menuBut, profileBut)
    menuKey.add(teamBut, usersBut)
    return menuKey


def YesNo():
    keyboard = InlineKeyboardMarkup()
    yesBut = InlineKeyboardButton(text="Да", callback_data="yes")
    noBut = InlineKeyboardButton(text="Нет", callback_data="no")
    keyboard.add(noBut, yesBut)
    return keyboard


def InlineInfo():
    keyboard = InlineKeyboardMarkup()
    trainingBut = InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
    infoBut = InlineKeyboardButton(text="Личная информация", callback_data="getuser")
    keyboard.add(trainingBut, infoBut)
    return keyboard


def InlineProfile(userId, chatId, team=None, profile=None):
    userId = str(userId)  # id пользователя
    chatId = str(chatId)
    is_admin = admin.Check(chatId)
    keyboard = InlineKeyboardMarkup()  # клавиатура с изменением настроек пользователя
    nameBut = InlineKeyboardButton(text="Фамилия Имя", callback_data="inline_profile_change_name_id" + userId)
    birthdayBut = InlineKeyboardButton(text="День рождения📅",
                                       callback_data="inline_profile_change_birthday_id" + userId)
    handleCFBut = InlineKeyboardButton(text="Хэндл📊",
                                     callback_data="inline_profile_change_handleCF_id" + userId)
    notificationsBut = InlineKeyboardButton(text="Уведомления🎺",
                                            callback_data="inline_profile_change_notifications_id" + userId)
    if not(profile):
        if team:
            backBut = InlineKeyboardButton(text="⬅️",
                                           callback_data="inline_profile_change_back_team_" + str(team))
        else:
            backBut = InlineKeyboardButton(text="⬅️",
                                           callback_data="inline_profile_change_back")
        keyboard.add(backBut)

    if userId != chatId:
        likeBut = InlineKeyboardButton(text="👍️",
                                       callback_data="inline_profile_change_like_" + userId)
        dislikeBut = InlineKeyboardButton(text="👎",
                                          callback_data="inline_profile_change_dislike_" + userId)
        keyboard.add(likeBut, dislikeBut)

    if is_admin or userId == chatId:
        keyboard.add(nameBut, birthdayBut)
        keyboard.add(handleCFBut, notificationsBut)
    if is_admin:
        handleHQBut = InlineKeyboardButton(text="Хэндл HQ", callback_data="inline_profile_change_handleHQ_id" + userId)
        participantBut = InlineKeyboardButton(text="Участник HQ", callback_data="inline_profile_change_is_participant_id" + userId)
        confirmationBut = InlineKeyboardButton(text="Подтвердить ✅", callback_data="inline_profile_change_confirmation_id" + userId)
        keyboard.add(confirmationBut)
        keyboard.add(handleHQBut, participantBut)
        if admin.MainAdmin(chatId):
            adminBut = InlineKeyboardButton(text="Админ 🔐", callback_data="inline_profile_change_admin_id" + userId)
            deleteBut = InlineKeyboardButton(text="Удалить ❌", callback_data="inline_profile_change_delete_id" + userId)
            keyboard.add(adminBut, deleteBut)
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


def InlineTeams(chatId):
    try:
        chatId = str(chatId)
        is_admin = admin.Check(chatId)
        keyboard = InlineKeyboardMarkup()  # клавиатура с командами

        teams = backend.get_teams({})
        sorted_teams = []
        for team in teams:
            sorted_teams.append([team['name'], team['number']])
        sorted_teams.sort()
        for team in sorted_teams:
            teamBut = InlineKeyboardButton(text=team[0],
                                           callback_data="inline_teams_team_number_" + team[1])
            keyboard.add(teamBut)

        if is_admin:
            newTeamBut = InlineKeyboardButton(text='Создать команду',
                                           callback_data="inline_teams_new_team")
            keyboard.add(newTeamBut)

        return keyboard
    except Exception as err:
        error.Log(errorAdminText='❗Произошла ошибка при создании клавиатуры с командами' + str(err))


def TeamSettings(chatId, teamNumber):
    try:
        chatId = str(chatId)
        is_admin = admin.Check(chatId)

        keyboard = InlineKeyboardMarkup()  # клавиатура команды
        team = backend.find_team(teamNumber)

        backBut = InlineKeyboardButton(text="⬅️",
                                       callback_data="inline_teams_settings_back")
        keyboard.add(backBut)

        good_users = []
        for user in team['participants']:
            info = backend.get_user(user)
            good_users.append([info['name'], user])
        good_users.sort()
        for user in good_users:
            nameBut = InlineKeyboardButton(text=user[0],
                                           callback_data="inline_users_id_team" + user[1] + '+' + str(team['number']))
            keyboard.add(nameBut)

        if is_admin is False:
            return keyboard

        addParticipantsBut = InlineKeyboardButton(text="Участники",
                                                  callback_data="inline_teams_settings_participants_" + str(team['number']))
        changeNameBut = InlineKeyboardButton(text="Название",
                                             callback_data="inline_teams_settings_change_name_" + str(team['number']))
        deleteBut = InlineKeyboardButton(text="Удалить ❌", callback_data="inline_teams_settings_delete_" + str(team['number']))

        keyboard.add(addParticipantsBut, changeNameBut)
        keyboard.add(deleteBut)
        return keyboard
    except Exception as err:
        error.Log(errorAdminText='❗Произошла ошибка при создании клавиатуры с настройками команды' + str(err))


def ParticipantsSettings(chatId, teamNumber):
    try:
        chatId = str(chatId)
        is_admin = admin.Check(chatId)
        if not is_admin:
            return
        team = backend.find_team(teamNumber)
        keyboard = InlineKeyboardMarkup()  # клавиатура с пользователями

        backBut = InlineKeyboardButton(text="⬅️",
                                       callback_data="inline_teams_settings_change_participants_back" + str(team['number']))
        keyboard.add(backBut)

        params = {'is_participant': True}
        backend_users = backend.get_users(params)
        good_users = []
        for user in backend_users:
            user_name = user['name'][: user['name'].find(' ')]
            new_user = [user_name, user['user_id']]
            if 'team' in user and user['team'] == teamNumber:
                new_user.append(2)
            elif 'team' in user and user['team'] is not None:
                new_user.append(1)
            else:
                new_user.append(0)
            good_users.append(new_user)
        good_users.sort()
        if len(good_users) % 2:
            good_users.append([' ', 'None'])
        line_count = len(good_users) // 2
        for i in range(line_count):
            def checkParticipant(isPatricipant):
                if isPatricipant == 2:
                    return ' ✅️'
                elif isPatricipant == 1:
                    return ' ☑️'
                else:
                    return ' ❌'
            user = good_users[i]
            leftBut = InlineKeyboardButton(text=user[0] + checkParticipant(user[2]),
                                           callback_data="inline_teams_settings_change_participant_id" + user[1] + '+' + str(team['number']))
            user = good_users[line_count + i]
            if user[1] == 'None':
                rightBut = InlineKeyboardButton(text=user[0], callback_data='Null')
            else:
                rightBut = InlineKeyboardButton(text=user[0] + checkParticipant(user[2]),
                                                callback_data="inline_teams_settings_change_participant_id" + user[1] + '+' + str(team['number']))
            keyboard.add(leftBut, rightBut)
        return keyboard
    except Exception as err:
        error.Log(errorAdminText='❗Произошла ошибка при создании клавиатуры с участниками команды' + str(err))