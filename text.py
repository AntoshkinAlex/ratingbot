import mongodb as backend
import admin

def SettingsInfo(userId, chatId):
    try:
        userId = str(userId)
        chatId = str(chatId)
        user = backend.get_user(userId)
        is_admin = admin.Check(chatId)
        is_confirmed = True

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
                    nonlocal is_confirmed
                    is_confirmed = False
                    return ' ⚠️'
            else:
                return ''

        fields = {
            'name': 'Фамилия Имя',
            'birthday': 'День рождения',
            'alias': 'Telegram',
            'codeforces_handle': 'Хэндл',
            'notifications': 'Уведомления',
            'handle': 'Хэндл HQ',
            'is_participant': 'Участник HQ',
            'is_admin': 'Админ'
        }

        text = "<b>Профиль пользователя:</b>\n\n"
        for field in fields:
            if (field == 'handle' or field == 'is_admin' or field == 'is_participant') and not(is_admin):
                continue
            if field == 'notifications' and not(is_admin) and userId != chatId:
                continue
            text += f"{fields[field]}: \t"
            if field == 'is_admin':
                text += '🟢' if admin.Check(userId) else '🔴'
            elif field in user and user[field] is not None or not(CheckConfirmationStatus(field)):
                if field == 'notifications' or field == 'is_participant':
                    text += '🟢' if user[field] else '🔴'
                else:
                    if field == 'alias':
                        text += f"{UnconfirmedText(field)}"
                    else:
                        text += f"<code>{UnconfirmedText(field)}</code>"
                    text += StatusFlag(field)
            else:
                text += f"<code>——</code>"
            text += "\n"

        if (is_admin or userId == chatId) and not is_confirmed:
            text += '\n⚠️ - ожидает подтверждения администратором️\n'

        return text
    except Exception as err:
        print(err, 'Произошла ошибка при сборке текста для настроек')

