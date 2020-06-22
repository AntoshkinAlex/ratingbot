import math
import index as req
import time
import const
import operator
import texttable as table
import mongodb as backend
import datetime
import requests
from bs4 import BeautifulSoup as BS
import pytz

bot = const.bot


def weather(now):
    try:
        rate = None
        try:
            r = requests.get('https://yandex.ru/news/quotes/2002.html')
            html = BS(r.content, 'html.parser')
            rate = html.find('td', {'class': 'quote__value'}).text
            rate = rate.replace(',', '.')
            rate = float(rate)
            print(rate)
            rate = round(rate * 100) / 100
            rate = str(rate)
        except Exception as err:
            print('Не удалось получить курс', err)

        r = requests.get('https://sinoptik.ua/погода-ставрополь')
        html = BS(r.content, 'html.parser')
        for el in html.select('#content'):
            t_min = el.select('.temperature .min')[0].text
            t_max = el.select('.temperature .max')[0].text
            text = el.select('.wDescription .description')[0].text
        t_min = t_min[t_min.find(' '): len(t_min)]
        t_max = t_max[t_max.find(' '): len(t_max)]
        while text[0] == ' ':
            text = text[1:len(text)]
        backend.add_weather(now)
        for user in backend.get_users({'notifications': True}):
            name = '!'
            if user['name'] != user['user_id']:
                name = ', ' + user['name'] + '!'
            mes = "Доброе утро" + name + "\n\n" + "Бот Сашка подготовил прогноз погоды на сегодня:\n\n" + \
                  "Мин. температура воздуха: " + str(t_min) + '\n' + "Макс. температура воздуха: " \
                  + str(t_max) + '\n\n' + str(text)

            if rate is not None:
                mes += '\n\nКурс ЦБ: 1$ = ' + rate + '₽'

            bot.send_message(user['user_id'], mes)
    except Exception as err:
        print('Не получилось сделать прогноз погоды', err)


def get_username(handle):
    return handle[handle.find("=") + 1:]


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
            if not (userName in const.users_handles):
                continue
            user_id = const.users_handles[userName]
            user_inf = backend.get_user(user_id)
            if not (user_inf['is_participant']):
                continue
            if not (user_id in users):
                users[user_id] = {}
                users[user_id]['rank'] = user['rank']
                users[user_id]['solved'] = [False for i in range(problemCount)]
                users[user_id]['upsolved'] = [False for i in range(problemCount)]
        for user in standings['result']['rows']:
            userName = user['party']['members'][0]['handle']
            if userName.find('=') == -1:
                continue
            userName = get_username(userName)
            if not (userName in const.users_handles):
                continue
            user_id = const.users_handles[userName]
            user_inf = backend.get_user(user_id)
            if not (user_inf['is_participant']):
                continue

            if user['rank'] != 0:
                users[user_id]['rank'] = user['rank']

            for index, problem in enumerate(user['problemResults']):
                if user['rank'] != 0:
                    if problem['points'] == 1:
                        users[user_id]['solved'][index] = True
                else:
                    if problem['points'] == 1:
                        users[user_id]['upsolved'][index] = True

        official = 0
        used = [0] * 200
        for user in users:
            user_inf = users[user]
            if user_inf['rank'] != 0:
                official += 1
                used[int(user_inf['rank'])] = user
            users[user]['solvedCount'], users[user]['upsolvedCount'] = get_solved_count(users[user]['solved'],
                                                                                        users[user]['upsolved'])
            maxSolved = max(maxSolved, users[user]['solvedCount'])

        top = 1
        for i in range(0, len(users)):
            if used[i] != 0:
                users[used[i]]['rank'] = top
                top += 1

        for user in users:
            users[user]['rating'] = get_contest_rating(users[user]['rank'], official, users[user]['solvedCount'],
                                                       maxSolved, users[user]['upsolvedCount'], problemCount)

        for user in backend.get_users({'is_participant': True}):
            user_id = user['user_id']
            if not (user_id in users):
                users[user_id] = {}
                users[user_id]['rank'] = 0
                users[user_id]['solvedCount'] = 0
                users[user_id]['upsolvedCount'] = 0
                users[user_id]['rating'] = 0
                users[user_id]['solved'] = [False for i in range(problemCount)]
                users[user_id]['upsolved'] = [False for i in range(problemCount)]

        contestInformation['users'] = users

        status = req.get_codeforces_contest_status(contestId, contest['apis'][0], contest['apis'][1])
        try:
            for submission in range(len(status['result']) - 1, -1, -1):
                name = get_username(status['result'][submission]['author']['members'][0]['handle'])
                if not (name in const.users_handles):
                    continue
                user_id = const.users_handles[name]
                user_inf = backend.get_user(user_id)
                if not (user_inf['is_participant']):
                    continue
                if status['result'][submission]['verdict'] == 'OK':
                    contestInformation['firstSubmission'] = {}
                    contestInformation['firstSubmission']['name'] = const.users_handles[get_username(
                        status['result'][submission]['author']['members'][0]['handle'])]
                    contestInformation['firstSubmission']['time'] = status['result'][submission][
                                                                        'relativeTimeSeconds'] // 60
                    break
        except Exception as err:
            print("Trouble with status", err)
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
                if contest['name'].find("Тренировка HQ №") != -1 and const.authors.count(contest['preparedBy']) != 0:
                    finished = False
                    if contest['phase'] == 'FINISHED':
                        finished = True
                    backend.update_contest(str(contest['id']),
                                           {
                                               'name': contest['name'],
                                               'apis': [const.apiKey[ind], const.apiSecret[ind]],
                                               'finished': finished
                                           })
                    contest_inf = backend.get_contest_information(contest['id'])
                    if not 'good_luck' in contest_inf or finished:
                        backend.update_contest(str(contest['id']), {'good_luck': finished})
                    if not 'reminder' in contest_inf or finished:
                        backend.update_contest(str(contest['id']), {'reminder': finished})
                    if contest['relativeTimeSeconds'] >= -600 and contest['phase'] == 'BEFORE' and not (
                            contest_inf['good_luck']):
                        backend.update_contest(str(contest['id']), {'good_luck': True})
                        good_luck()
                    if contest['relativeTimeSeconds'] >= -61200 and contest['phase'] == 'BEFORE' and not (
                            contest_inf['reminder']):
                        backend.update_contest(str(contest['id']), {'reminder': True})
                        reminder()
    except:
        print('CF UPAL')


def take_contests():
    while True:
        try:
            now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            if now.hour >= 9:
                now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
                now = str(now)
                now = now[0:now.find(' ')]
                if backend.find_weather(now) is None:
                    weather(now)
            get_hq_contests()
            get_contest()
            get_user_infomation()
            get_all_rating()
            time.sleep(300)
        except Exception as err:
            print("Ошибка при обновлении бота", err)
            time.sleep(300)


def get_user_infomation():
    try:
        user_information = {}
        contest = {}
        for contest_inf in backend.get_contests():
            contestId = contest_inf['contest_id']
            contest[contestId] = {}
            contest[contestId] = backend.get_contest_information(contestId)

        for user in backend.get_users({'is_participant': True}):
            user_id = user['user_id']
            user_information[user_id] = {}
            user_information[user_id]['name'] = backend.get_user(user_id)['name']
            user_information[user_id]['achievements'] = ''
            unsolvedCount = 0
            solvedCount = 0
            solvedCountLast = 0
            allCount = 0
            user_div = backend.get_user(user_id)['division']
            for (index, contest_inf) in enumerate(backend.get_contests()):
                contestId = contest_inf['contest_id']
                if user_id in contest[contestId]['users']:
                    unsolvedCount += contest[contestId]['problemCount'] - \
                                     (contest[contestId]['users'][user_id]['solvedCount'] +
                                      contest[contestId]['users'][user_id]['upsolvedCount'])
                    solvedCount += contest[contestId]['users'][user_id]['solvedCount'] + \
                                   contest[contestId]['users'][user_id][
                                       'upsolvedCount']
                    rank = contest[contestId]['users'][user_id]['rank']
                    if rank == 1:
                        user_information[user_id]['achievements'] += "🥇"
                    elif rank == 2:
                        user_information[user_id]['achievements'] += "🥈"
                    elif rank == 3:
                        user_information[user_id]['achievements'] += "🥉"
                    if len(contest) - index <= 5:
                        solvedCountLast += contest[contestId]['users'][user_id]['solvedCount'] + \
                                           contest[contestId]['users'][user_id]['upsolvedCount']
                        allCount += contest[contestId]['problemCount']
                else:
                    unsolvedCount += contest[contestId]['problemCount']
                    if len(contest) - index <= 5:
                        allCount += contest[contestId]['problemCount']

            user_inf = backend.get_user(user_id)
            if user_information[user_id]['achievements'] == '' and (
                    'custom_achievements' in user_inf and len(user_inf['custom_achievements']) == 0 or not (
                    'custom_achievements' in user_inf)):
                user_information[user_id]['achievements'] = 'Пока тут ничего нет :('
            user_information[user_id]['solved'] = solvedCount
            user_information[user_id]['unsolved'] = unsolvedCount
            user_information[user_id]['activity'] = ''
            user_information[user_id]['solvedLast'] = solvedCountLast
            user_information[user_id]['allLast'] = allCount
            activity = solvedCountLast / allCount * 100

            if user_div == 2:
                if activity >= 75:
                    user_information[user_id]['activity'] = '🟣 Очень высокий уровень активности'
                elif activity >= 69:
                    user_information[user_id]['activity'] = '🟢 Высокий уровень активности'
                elif activity >= 62:
                    user_information[user_id]['activity'] = '🟡 Средний уровень активности'
                elif activity >= 57:
                    user_information[user_id]['activity'] = '🟠 Низкий уровень активности'
                else:
                    user_information[user_id]['activity'] = '🔴 Очень низкий уровень активности'
            else:
                if activity >= 95:
                    user_information[user_id]['activity'] = '🟣 Очень высокий уровень активности'
                elif activity >= 85:
                    user_information[user_id]['activity'] = '🟢 Высокий уровень активности'
                elif activity >= 75:
                    user_information[user_id]['activity'] = '🟡 Средний уровень активности'
                elif activity >= 67:
                    user_information[user_id]['activity'] = '🟠 Низкий уровень активности'
                else:
                    user_information[user_id]['activity'] = '🔴 Очень низкий уровень активности'
            user_information[user_id]['active_name'] = user_information[user_id]['name'] + ' ' + \
                                                       user_information[user_id]['activity'][0]
            user_information[user_id]['percent'] = math.floor(activity)
            updates = user_information[user_id]
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
        for user in backend.get_users({'is_participant': True}):
            handle = user['user_id']
            hq_rating[handle] = 0
            solved[handle] = 0
            upsolved[handle] = 0

        for contest in backend.get_contests():
            for user in contest['users']:
                is_participant = backend.get_user(user)['is_participant']
                if is_participant:
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
                userName = backend.get_user(user)['name']
                name = userName[userName.find(' ') + 1:]
                if index == 9:
                    space = ' '
                print_rating.add_row([str(index + 1) + space +
                                      name,
                                      str(hq_rating_information[user]['rating']),
                                      str(hq_rating_information[user]['upsolved'] + hq_rating_information[user][
                                          'solved'])
                                      ])
            backend.update_rating({'rating': print_rating.draw()})
        except Exception as err:
            print("Не удалось получить таблицу рейтинга", err)
    except Exception as err:
        print('Не удалось получить общий рейтинг', err)


def declension(number, dec1, dec2, dec3):
    if 11 <= number % 100 and number % 100 <= 19:
        return dec3
    if number % 10 == 1:
        return dec1
    if 2 <= number % 10 and number % 10 <= 4:
        return dec2
    return dec3
