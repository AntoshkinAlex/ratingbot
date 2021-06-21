import const

bot = const.bot

def Log(adminId=const.mainAdmin, errorAdminText=None, userId=None, errorUserText=None):
    if errorAdminText is not None:
        print(errorAdminText)
        bot.send_message(adminId, errorAdminText)
    if userId is not None:
        bot.send_message(userId, errorUserText)
