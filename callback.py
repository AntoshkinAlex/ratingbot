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
