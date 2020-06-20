import math

import index as req
from threading import Thread
import time
import const
import operator
import texttable as table
from functools import cmp_to_key
import mongodb as backend

bot = const.bot

def get_username(handle):
    return handle[handle.find("=") + 1 : ]


def get_contest_rating(place, userCount, solved, maxSolved, upsolved, problemCount):
    rating = (200 * (userCount - place + 1) / userCount) * (solved / maxSolved) + 100 * upsolved / problemCount
    return round(rating)


def get_solved_count(solved, upsolved):
    solvedCount = 0
    upsolvedCount = 0
    for i in range(len(solved)):
        if solved[i]:
            solvedCount += 1
        elif upsolved[i]:
            upsolvedCount += 1
    return solvedCount, upsolvedCount


def get_contest_information(contestId):
    try:
        contestId = str(contestId)
        contest = backend.get_contest_information(contestId)
        standings = req.get_codeforces_contest_stadings(contestId, contest['apis'][0], contest['apis'][1], True)
        contestInformation = {}
        contestInformation['name'] = req.get_contestName(contestId, contest['apis'][0], contest['apis'][1])

        users = {}
        maxSolved = 1
        problemCount = len(standings['result']['problems'])
        contestInformation['problemCount'] = problemCount

        for user in standings['result']['rows']:
            userName = user['party']['members'][0]['handle']
            userName = get_username(userName)
            if not (userName in const.handles):
                continue
            if not(userName in users):
                users[userName] = {}
            users[userName]['rank'] = user['rank']
            users[userName]['solved'] = [False for i in range(problemCount)]
            users[userName]['upsolved'] = [False for i in range(problemCount)]

        for user in standings['result']['rows']:
            userName = user['party']['members'][0]['handle']
            if not (get_username(userName) in const.handles):
                continue
            if userName.find('=') == -1:
                continue
            if user['rank'] != 0:
                users[get_username(userName)]['rank'] = user['rank']
            for index, problem in enumerate(user['problemResults']):
                if user['rank'] != 0:
                    if problem['points'] == 1:
                        users[get_username(userName)]['solved'][index] = True
                else:
                    if problem['points'] == 1:
                        users[get_username(userName)]['upsolved'][index] = True
        for user in users:
            users[user]['solvedCount'], users[user]['upsolvedCount'] = get_solved_count(users[user]['solved'],  users[user]['upsolved'])
            maxSolved = max(maxSolved, users[user]['solvedCount'])
        for user in users:
            users[user]['rating'] = get_contest_rating(users[user]['rank'], len(users),  users[user]['solvedCount'], maxSolved,  users[user]['upsolvedCount'], problemCount)
        for user in const.handles:
            if not(user in users):
                users[user] = {}
                users[user]['rank'] = 0
                users[user]['solvedCount'] = 0
                users[user]['upsolvedCount'] = 0
                users[user]['rating'] = 0
                users[user]['solved'] = [False for i in range(problemCount)]
                users[user]['upsolved'] = [False for i in range(problemCount)]


        contestInformation['users'] = users

        status = req.get_codeforces_contest_status(contestId, contest['apis'][0], contest['apis'][1])
        try:
            for submission in range(len(status['result']) - 1, -1, -1):
                name = get_username(status['result'][submission]['author']['members'][0]['handle'])
                if status['result'][submission]['verdict'] == 'OK' and (name in const.handles):
                    contestInformation['firstSubmission'] = {}
                    contestInformation['firstSubmission']['name'] = get_username(status['result'][submission]['author']['members'][0]['handle'])
                    contestInformation['firstSubmission']['time'] = status['result'][submission]['relativeTimeSeconds'] // 60
                    break
        except:
            print("Trouble with status")
        backend.update_contest(contestId, contestInformation)
    except Exception as err:
        print("Failed Contest Information", err)


def get_first_three_place(contestId):
    try:
        contestInfomation = backend.get_contest_information(contestId)
        cnt = 0
        firstPlaces = []
        for user in contestInfomation['users']:
            if contestInfomation['users'][user]['rank'] != 0:
                firstPlaces.append([user, contestInfomation['users'][user]['solvedCount']])
                cnt += 1
            if cnt == 3:
                break
        backend.update_contest(contestId, {'contestTop': firstPlaces})
    except:
        print('Не удалось взять топ 3')


def good_luck():
    for user in const.users:
        bot.send_message(user, "Бот Сашка желает тебе удачи на контесте! 🏆")

def reminder():
    for user in const.users:
        bot.send_message(user, "Бот Сашка напоминает вам о том, что до начала контеста осталось меньше 17 часов! 🖥")

def get_hq_contests():
    try:
        for ind in range(2):
            hq_contest = req.get_codeforces_contest_list(const.apiKey[ind], const.apiSecret[ind], True)
            for contest in hq_contest['result']:
                if contest['name'].find("Тренировка HQ №") != -1 and const.authors.count(contest['preparedBy']) != 0\
                        and contest['phase'] == 'FINISHED':
                    backend.update_contest(str(contest['id']), {'name': contest['name'], 'apis': [const.apiKey[ind], const.apiSecret[ind]]})
                if contest['name'].find("Тренировка HQ №") != -1 and const.authors.count(contest['preparedBy']) != 0\
                        and contest['relativeTimeSeconds'] >= -600 and contest['phase'] == 'BEFORE' and not(contest['id'] in const.goodluck):
                    const.goodluck.append(contest['id'])
                   # good_luck()
                if contest['name'].find("Тренировка HQ №") != -1 and const.authors.count(contest['preparedBy']) != 0\
                        and contest['relativeTimeSeconds'] >= -61200 and contest['phase'] == 'BEFORE' and not(contest['id'] in const.reminder):
                    const.reminder.append(contest['id'])
                 #   reminder()
    except:
        print('CF UPAL')


def take_contests():
    while True:
        try:
            get_hq_contests()
            get_contest()
            get_user_infomation()
            get_all_rating()
            time.sleep(300)
        except:
            time.sleep(300)


def get_user_infomation():
    try:
        user_information = {}
        contest = {}
        for contest_inf in backend.get_contests():
            contestId = contest_inf['contest_id']
            contest[contestId] = {}
            contest[contestId] = backend.get_contest_information(contestId)

        for user in const.handles:
            user_information[user] = {}
            user_information[user]['name'] = const.handles[user]
            user_information[user]['achievements'] = ''
            unsolvedCount = 0
            solvedCount = 0
            solvedCountLast = 0
            allCount = 0
            for (index, contestId) in enumerate(contest):
                if user in contest[contestId]['users']:
                    unsolvedCount += contest[contestId]['problemCount'] - \
                        (contest[contestId]['users'][user]['solvedCount'] + contest[contestId]['users'][user]['upsolvedCount'])
                    solvedCount += contest[contestId]['users'][user]['solvedCount'] + contest[contestId]['users'][user]['upsolvedCount']
                    rank = contest[contestId]['users'][user]['rank']
                    if rank == 1:
                        user_information[user]['achievements'] += "🥇"
                    elif rank == 2:
                        user_information[user]['achievements'] += "🥈"
                    elif rank == 3:
                        user_information[user]['achievements'] += "🥉"
                    if len(contest) - index <= 5:
                        solvedCountLast += contest[contestId]['users'][user]['solvedCount'] + contest[contestId]['users'][user]['upsolvedCount']
                        allCount += contest[contestId]['problemCount']
                else:
                    unsolvedCount += contest[contestId]['problemCount']
                    if len(contest) - index <= 5:
                        allCount += contest[contestId]['problemCount']
            if user_information[user]['achievements'] == '' and const.userAchievements[user] == '':
                user_information[user]['achievements'] = 'Пока тут ничего нет :('
            user_information[user]['solved'] = solvedCount
            user_information[user]['unsolved'] = unsolvedCount
            user_information[user]['activity'] = ''
            user_information[user]['solvedLast'] = solvedCountLast
            user_information[user]['allLast'] = allCount
            activity = solvedCountLast / allCount * 100
            if user in const.first_course:
                if activity >= 75:
                    user_information[user]['activity'] = '🟣 Очень высокий уровень активности'
                elif activity >= 69:
                    user_information[user]['activity'] = '🟢 Высокий уровень активности'
                elif activity >= 62:
                    user_information[user]['activity'] = '🟡 Средний уровень активности'
                elif activity >= 57:
                    user_information[user]['activity'] = '🟠 Низкий уровень активности'
                else:
                    user_information[user]['activity'] = '🔴 Очень низкий уровень активности'
            else:
                if activity >= 95:
                    user_information[user]['activity'] = '🟣 Очень высокий уровень активности'
                elif activity >= 85:
                    user_information[user]['activity'] = '🟢 Высокий уровень активности'
                elif activity >= 75:
                    user_information[user]['activity'] = '🟡 Средний уровень активности'
                elif activity >= 67:
                    user_information[user]['activity'] = '🟠 Низкий уровень активности'
                else:
                    user_information[user]['activity'] = '🔴 Очень низкий уровень активности'
            user_information[user]['name'] += ' ' + user_information[user]['activity'][0]
            user_information[user]['percent'] = math.floor(activity)
            user_id = const.users_handles[user]
            backend.insert_user(user_id, '', '')
            updates = user_information[user]
            backend.update_user(user_id, updates)
    except Exception as err:
        print('Не удалось взять личную информацию пользователей', err)


def get_sortedRating(contestId):
    contest_information = backend.get_contest_information(contestId)
    sortedRating = []
    for user in contest_information['users']:
        sortedRating.append(
            [contest_information['users'][user]['rating'], user]
        )
    sortedRating.sort()
    sortedRating.reverse()
    backend.update_contest(contestId, {'sortedRating': sortedRating})


def get_contest():
    try:
        for contest in backend.get_contests():
            contestId = contest['contest_id']
            get_contest_information(contestId)
            get_first_three_place(contestId)
            get_sortedRating(contestId)
    except Exception as err:
        print('Ошибка при получении информации о контесте', err)


def get_all_rating():
    global print_rating
    try:
        hq_rating = {}
        solved = {}
        upsolved = {}
        for handle in const.handles.keys():
            hq_rating[handle] = 0
            solved[handle] = 0
            upsolved[handle] = 0

        for contest in backend.get_contests():
            for user in contest['users']:
                if user in const.handles:
                    hq_rating[user] += contest['users'][user]['rating']
                    solved[user] += contest['users'][user]['solvedCount']
                    upsolved[user] += contest['users'][user]['upsolvedCount']

        hq_rating = sorted(hq_rating.items(), key=operator.itemgetter(1))
        hq_rating.reverse()

        hq_rating_information = {}
        
        for item in hq_rating:
            user = item[0]
            hq_rating_information[user] = {}
            hq_rating_information[user]['solved'] = solved[user]
            hq_rating_information[user]['upsolved'] = upsolved[user]
            hq_rating_information[user]['rating'] = item[1]
        try:
            print_rating = table.Texttable()
            print_rating.set_deco(table.Texttable.HEADER)
            print_rating.set_cols_align(["l", "c", "c"])
            print_rating.set_cols_valign(["t", "t", "m"])
            print_rating.set_cols_dtype(['t', 'i', 'i'])
            print_rating.add_row(["Фамилия\n", "🏆\n", "Задачи\n"])
        except:
            print('Ошибка при выводе топа рейтинга')
        try:
            space = '  '
            for index, user in enumerate(hq_rating_information):
                userName = str(const.handles[user])
                name = userName[userName.find(' ') + 1:]
                if index == 9:
                    space = ' '
                print_rating.add_row([str(index + 1) + space +
                    name,
                    str(hq_rating_information[user]['rating']),
                    str(hq_rating_information[user]['upsolved'] + hq_rating_information[user]['solved'])
                ])
            backend.update_rating({'rating': print_rating.draw()})
        except Exception as err:
            print("Не удалось получить таблицу рейтинга", err)
    except Exception as err:
        print('Не удалось получить общий рейтинг', err)


def declension(number, dec1, dec2, dec3):
    if (11 <= number % 100 and number % 100 <= 19):
        return dec3
    if (number % 10 == 1):
        return dec1
    if (2 <= number % 10 and number % 10 <= 4):
        return dec2
    return dec3




#print(get_hq_contest())
#print(get_contest_information(273749))
#print(get_first_three_place(273749))