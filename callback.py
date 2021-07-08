from threading import Thread
import telebot
import structure as struct
import index as req
import const
import admin
import texttable as table
import mongodb as backend
import re
import error
import text
import keyboard

bot = const.bot


def InlineProfile(data, callback):
    fields = {
        'name_id': 'Введите через пробел фамилию и имя.',
        'birthday_id': 'Введите дату рождения в следующем формате без кавычек "День.Mесяц.Год".',
        'alias_id': 'Введите Telegram username в следующем формате без кавычек "@username".',
        'handleCF_id': 'Введите хэндл с Codeforces.',
        'handleHQ_id': 'Введите хэндл с HQ Contests.',
        'confirmation_id': 'Чтобы подтвердить все поля, нажмите на /confirm.\n'
                           'Чтобы отклонить все поля, нажмите /reject.\n'
                           'Если человек неправильно заполнил одно из полей, напишите ему, чтобы он это исправил.\n'
    }
    state = [
        'notifications_id',
        'is_participant_id',
    ]

    if re.match('delete_id', callback) is not None:
        try:
            user_id = re.split('delete_id', callback, maxsplit=1)[1]
            chat_id = data.from_user.id
            message_id = bot.send_message(chat_id,
                                          'Напишите 12345, если хотите удалить пользователя. '
                                          + ' Для отмены нажмите на /cancel.').message_id
            backend.insert_session(chat_id, 'inline_profile_change_' + 'delete',
                                   {'user_id': user_id, 'delete': message_id})
        except Exception as err:
            error.Log(errorAdminText='❗Произошла ошибка при удалении пользователя ' + str(err))
    elif re.match('admin_id', callback) is not None:
        try:
            user_id = re.split('admin_id', callback, maxsplit=1)[1]
            chat_id = data.from_user.id
            if admin.Check(user_id):
                backend.delete_admin(user_id)
            else:
                backend.insert_admin(user_id)
            new_text = text.SettingsInfo(user_id, chat_id)
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=data.message.message_id, text=new_text,
                                      reply_markup=keyboard.InlineProfile(user_id, chat_id), parse_mode='html')
            except:
                ...
        except Exception as err:
            error.Log(errorAdminText='❗Произошла ошибка при изменении администрирования пользователя ' + str(err))
    elif re.match('back', callback) is not None:
        try:
            chat_id = data.from_user.id
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=data.message.message_id, text='Выберите пользователя:',
                                      reply_markup=keyboard.InlineUsers(chat_id))
            except:
                ...
        except Exception as err:
            error.Log(errorAdminText='❗Произошла ошибка при изменении возвращении к списку пользователей ' + str(err))

    for field in fields:
        if re.match(field, callback) is not None:
            def change_field(message, chat_id):
                try:
                    user_id = re.split(field, message, maxsplit=1)[1]
                    message_id = bot.send_message(chat_id,
                                                  fields[field] + ' Для отмены нажмите на /cancel.').message_id
                    backend.insert_session(chat_id, 'inline_profile_change_' + field[:field.find('_')],
                                           {'user_id': user_id, 'message_id': data.message.message_id,
                                            'delete': message_id})
                except Exception as err:
                    error.Log(errorAdminText='❗Произошла ошибка при выводе сообщения об изменении ' + field + ' ' + str(err),
                              userId=chat_id, errorUserText='Произошла ошибка')
            change_field(callback, data.from_user.id)
    for field in state:
        if re.match(field, callback) is not None:
            def change_field(message, chat_id):
                try:
                    user_id = re.split(field, message, maxsplit=1)[1]
                    user = backend.get_user(user_id)
                    new_field = field[:field.rfind('_')]
                    if new_field == 'is_participant' and not(admin.Check(chat_id)):
                        bot.send_message(chat_id, 'Вы не админ.')
                        return
                    backend.update_user(user_id, {new_field: not(user[new_field])})
                    new_text = text.SettingsInfo(user_id, chat_id)
                    try:
                        bot.edit_message_text(chat_id=chat_id, message_id=data.message.message_id, text=new_text,
                                              reply_markup=keyboard.InlineProfile(user_id, chat_id), parse_mode='html')
                    except:
                        ...
                except Exception as err:
                    error.Log(errorAdminText='❗Произошла ошибка при изменении состояния ' + field + ' ' + str(err),
                              userId=chat_id, errorUserText='Произошла ошибка')
            change_field(callback, str(data.from_user.id))


def InlineTeams(data, callback):
    chat_id = data.from_user.id
    is_admin = admin.Check(chat_id)
    if re.match('new_team', callback) is not None and is_admin:
        if backend.find_team('Новая команда') is not None:
            bot.send_message(chat_id, 'Новая команда уже создана. Измените её название, чтобы создать ещё одну команду.')
            return
        backend.insert_team()
        message_id = bot.send_message(chat_id, 'Введите название команды').message_id
        backend.insert_session(chat_id=chat_id, name='inline_teams_change_name',
                               args={'teamName': 'Новая команда', 'delete': message_id, 'message_id': data.message.id})
    elif re.match('team_name', callback) is not None:
        name = re.split('team_name_', callback, maxsplit=1)[1]
        team = backend.find_team(name)
        if team is None:
            bot.send_message(chat_id=chat_id, text='Такой команды больше не существует.')
            return
        bot.send_message(chat_id=chat_id, text='Тут будет инфа о команде ' + team['name'],
                         reply_markup=keyboard.TeamSettings(chat_id, team))

    elif re.match('settings_participants', callback) is not None:
        name = re.split('settings_participants_', callback, maxsplit=1)[1]
        team = backend.find_team(name)
        bot.send_message(chat_id=chat_id, text='Тут будут настройки')
    elif re.match('settings_change_name', callback) is not None:
        name = re.split('settings_change_name_', callback, maxsplit=1)[1]
        team = backend.find_team(name)
        message_id = bot.send_message(chat_id, 'Введите новое название команды. Для отмены введите /cancel.').message_id
        backend.insert_session(chat_id=chat_id, name='inline_teams_change_name',
                               args={'teamName': team['name'], 'delete': message_id, 'message_id': data.message.id})
    elif re.match('settings_delete', callback) is not None:
        name = re.split('settings_delete_', callback, maxsplit=1)[1]
        team = backend.find_team(name)
        message_id = bot.send_message(chat_id=chat_id, text='Вы точно хотите удалить команду?',
                                      reply_markup=keyboard.YesNo()).message_id
        backend.insert_session(chat_id=chat_id, name='inline_teams_settings_delete',
                               args={'teamName': team['name'], 'delete': message_id, 'message_id': data.message.id})