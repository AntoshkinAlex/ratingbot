import index as req
from threading import Thread
import time
import const
import operator
import texttable as table
from functools import cmp_to_key

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
        standings = req.get_codeforces_contest_stadings(contestId, const.apis[contestId][0], const.apis[contestId][1], True)
        contestInformation = {}
        contestInformation['name'] = req.get_contestName(contestId, const.apis[contestId][0], const.apis[contestId][1])

        users = {}
        maxSolved = 1
        problemCount = len(standings['result']['problems'])
        contestInformation['problemCount'] = problemCount

        for user in standings['result']['rows']:
            userName = user['party']['members'][0]['handle']
            if not (get_username(userName) in const.handles):
                continue
            if not(get_username(userName) in users):
                users[get_username(userName)] = {}
            users[get_username(userName)]['rank'] = user['rank']
            users[get_username(userName)]['solved'] = [False for i in range(problemCount)]
            users[get_username(userName)]['upsolved'] = [False for i in range(problemCount)]

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

        status = req.get_codeforces_contest_status(contestId, const.apis[contestId][0], const.apis[contestId][1])
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
        return contestInformation
    except Exception as err:
        print("Failed Contest Information", err)


def get_first_three_place(contestId):
    try:
        contestInfomation = get_contest_information(contestId)
        cnt = 0
        firstPlaces = []
        for user in contestInfomation['users']:
            if contestInfomation['users'][user]['rank'] != 0:
                firstPlaces.append([user, contestInfomation['users'][user]['solvedCount']])
                cnt += 1
            if cnt == 3:
                break
        return firstPlaces
    except:
        print('Не удалось взять топ 3')


def comparator(contestId1, contestId2):
    contestName = req.get_contestName(contestId1, const.apis[str(contestId1)][0], const.apis[str(contestId1)][1])
    const.name_id_contests[contestId1] = contestName
    contestNum1 = int(contestName[15 : ])
    contestName = req.get_contestName(contestId2, const.apis[str(contestId2)][0], const.apis[str(contestId2)][1])
    const.name_id_contests[contestId2] = contestName
    contestNum2 = int(contestName[15 : ])
    return contestNum1 - contestNum2


def get_hq_contests():
    try:
        name_contests = {}
        apis = {}
        for ind in range(2):
            hq_contest = req.get_codeforces_contest_list(const.apiKey[ind], const.apiSecret[ind], True)
            for contest in hq_contest['result']:
                if contest['name'].find("Тренировка HQ №") != -1 and const.authors.count(contest['preparedBy']) != 0\
                        and contest['phase'] == 'FINISHED':
                    name_contests[contest['name']] = (str(contest['id']))
                    apis[str(contest['id'])] = [const.apiKey[ind], const.apiSecret[ind]]
        #print('O VSTAL')
        const.name_contests = name_contests
        const.apis = apis
        return [const.name_contests, const.apis]
    except:
        print('CF UPAL')


def take_contests():
    while True:
        try:
            temp = get_hq_contests()
            hq_contests = []
            for id in const.name_contests:
                hq_contests.append(const.name_contests[id])
            const.hq_contests = sorted(hq_contests, key=cmp_to_key(comparator))
            const.apis = temp[1]
            get_contest()
            get_user_infomation()
            get_all_rating()
            time.sleep(300)
        except:
            time.sleep(180)


def get_user_infomation():
    try:
        user_information = {}
        contest = {}
        for contestId in const.hq_contests:
            contest[contestId] = {}
            contest[contestId] = get_contest_information(contestId)
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
                    if len(const.hq_contests) - index <= 5:
                        solvedCountLast += contest[contestId]['users'][user]['solvedCount'] + contest[contestId]['users'][user]['upsolvedCount']
                        allCount += contest[contestId]['problemCount']
                else:
                    unsolvedCount += contest[contestId]['problemCount']
                    if len(const.hq_contests) - index <= 5:
                        allCount += contest[contestId]['problemCount']
            if user_information[user]['achievements'] == '':
                user_information[user]['achievements'] = 'Пока тут ничего нет :('
            user_information[user]['solved'] = solvedCount
            user_information[user]['unsolved'] = unsolvedCount
            user_information[user]['activity'] = ''
            activity = solvedCountLast / allCount * 100
            if user in const.first_course:
                if activity >= 75:
                    user_information[user]['activity'] = '🟣 Очень высокий уровень активности'
                elif activity >= 65:
                    user_information[user]['activity'] = '🟢 Высокий уровень активности'
                elif activity >= 57:
                    user_information[user]['activity'] = '🟡 Средний уровень активности'
                elif activity >= 50:
                    user_information[user]['activity'] = '🟠 Низкий уровень активности'
                else:
                    user_information[user]['activity'] = '🔴 Очень низкий уровень активности'
            else:
                if activity >= 95:
                    user_information[user]['activity'] = '🟣 Очень высокий уровень активности'
                elif activity >= 85:
                    user_information[user]['activity'] = '🟢 Высокий уровень активности'
                elif activity >= 70:
                    user_information[user]['activity'] = '🟡 Средний уровень активности'
                elif activity >= 60:
                    user_information[user]['activity'] = '🟠 Низкий уровень активности'
                else:
                    user_information[user]['activity'] = '🔴 Очень низкий уровень активности'

            user_information[user]['name'] += ' ' + user_information[user]['activity'][0]

        const.user_information = user_information
    except:
        print('Не удалось взять личную информацию пользователей')



def get_contest():
    try:
        hq_contest_information = {}
        for contestId in const.hq_contests:
            hq_contest_information[contestId] = {}
            hq_contest_information[contestId]['contest'] = get_contest_information(contestId)
            hq_contest_information[contestId]['contestTop'] = get_first_three_place(contestId)
            hq_contest_information[contestId]['sortedRating'] = []
            for user in hq_contest_information[contestId]['contest']['users']:
                hq_contest_information[contestId]['sortedRating'].append(
                    [hq_contest_information[contestId]['contest']['users'][user]['rating'], user]
                )
            hq_contest_information[contestId]['sortedRating'].sort()
            hq_contest_information[contestId]['sortedRating'].reverse()
        const.hq_contest_information = hq_contest_information
    except:
        print('Ошибка при получении информации о контесте')


def get_all_rating():
    try:
        hq_rating = {}
        solved = {}
        upsolved = {}
        for handle in const.handles.keys():
            hq_rating[handle] = 0
            solved[handle] = 0
            upsolved[handle] = 0

        for contestId in const.hq_contests:
            contestInfomation = get_contest_information(contestId)
            for user in contestInfomation['users']:
                if (user in const.handles):
                    hq_rating[user] += contestInfomation['users'][user]['rating']
                    solved[user] += contestInfomation['users'][user]['solvedCount']
                    upsolved[user] += contestInfomation['users'][user]['upsolvedCount']

        hq_rating = sorted(hq_rating.items(), key=operator.itemgetter(1))
        hq_rating.reverse()

        const.hq_rating_information = {}
        
        for item in hq_rating:
            user = item[0]
            const.hq_rating_information[user] = {}
            const.hq_rating_information[user]['solved'] = solved[user]
            const.hq_rating_information[user]['upsolved'] = upsolved[user]
            const.hq_rating_information[user]['rating'] = item[1]
        try:
            print_rating = table.Texttable()
            print_rating.set_deco(table.Texttable.HEADER)
            print_rating.set_cols_align(["l", "c", "c"])
            print_rating.set_cols_valign(["t", "t", "m"])
            print_rating.set_cols_dtype(['t', 'i', 'i'])
            print_rating.add_row(["Фамилия\n", "🏆\n", "Задачи\n"])
            space = '  '
        except:
            print('Ошибка при выводе топа рейтинга')
        try:
            for index, user in enumerate(const.hq_rating_information):
                userName = str(const.handles[user])
                name = userName[userName.find(' ') + 1:]
                if (index == 9):
                    space = ' '
                print_rating.add_row([str(index + 1) + space +
                    name,
                    str(const.hq_rating_information[user]['rating']),
                    str(const.hq_rating_information[user]['solved'] + const.hq_rating_information[user]['upsolved'])
                ])
                const.all_rating = print_rating
        except:
            print("Не удалось получить общий рейтинг")

    except:
        print('Не удалось получить общий рейтинг')


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