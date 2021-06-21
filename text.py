import mongodb as backend
import admin

def SettingsInfo(userId, chatId):
    try:
        userId = str(userId)
        chatId = str(chatId)
        user = backend.get_user(userId)
        is_admin = admin.Check(chatId)

        def CheckConfirmationStatus(key):
            if 'confirmation' in user and key in user['confirmation'] and (is_admin or userId == chatId):
                return False
            else:
                return True

        def UnconfirmedText(key):
            if not (CheckConfirmationStatus(key)):
                return str(user['confirmation'][key])
            else:
                return str(user[key])

        def StatusFlag(key):
            if is_admin or userId == chatId:
                if CheckConfirmationStatus(key):
                    return ' ✅'
                else:
                    return ' ⚠️'
            else:
                return ''

        fields = {
            'name': 'Фамилия Имя',
            'birthday': 'Дата рождения',
            'alias': 'Telegram username',
            'codeforces_handle': 'Хэндл на Сodeforces',
            'notifications': 'Ежедневные уведомления',
            'handle': 'Хэндл на HQ Contest',
            'is_participant': 'Участник HQ',
            'is_admin': 'Является админом'
        }

        text = "*Профиль пользователя:*\n\n"
        for field in fields:
            if (field == 'handle' or field == 'is_admin') and not(is_admin):
                continue
            text += f"{fields[field]}: "
            if field == 'is_admin':
                text += '🟢' if admin.Check(userId) else '🔴'
                continue
            if field in user and user[field] is not None or not(CheckConfirmationStatus(field)):
                if field == 'notifications' or field == 'is_participant' or field == 'is_admin':
                    text += '🟢' if user[field] else '🔴'
                else:
                    text += f"`{UnconfirmedText(field)}`{StatusFlag(field)}"
            else:
                text += '`——`'
            text += "\n"

        if is_admin or userId == chatId:
            text += '\n⚠️ - ожидает подтверждения администратором️\n'

        text += ' '  # пустой символ, чтобы не удалялся перевод строки в конце

        pos = 0
        while text.find('-', pos) != pos and text.find('-', pos) != -1:  # в telegram зарезервирован '-', нужно перед ним добавить '\' (все хэндлы с дефисом # пишутся)
            pos = text.find('-', pos)
            text = text[:pos] + '\-' + text[pos + 1:]
            pos += 2

        return text
    except Exception as err:
        print(err, 'Произошла ошибка при сборке текста для настроек')
