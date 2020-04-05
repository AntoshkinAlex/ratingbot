import index as req
from threading import Thread
import time
import const
import operator
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
    contestId = str(contestId)
    standings = req.get_codeforces_contest_stadings(contestId, const.apis[contestId][0], const.apis[contestId][1], True)
    contestInformation = {}
    contestInformation['name'] = req.get_contestName(contestId, const.apis[contestId][0], const.apis[contestId][1])

    users = {}
    maxSolved = 1
    problemCount = len(standings['result']['problems'])

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


def get_first_three_place(contestId):
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

def comparator(contestId1, contestId2):
    contestName = req.get_contestName(contestId1, const.apis[str(contestId1)][0], const.apis[str(contestId1)][1])
    contestNum1 = int(contestName[15 : ])
    contestName = req.get_contestName(contestId2, const.apis[str(contestId2)][0], const.apis[str(contestId2)][1])
    contestNum2 = int(contestName[15 : ])
    return contestNum1 - contestNum2


def get_hq_contests():
    #try:
        contests = []
        apis = {}
        for ind in range(2):
            hq_contest = req.get_codeforces_contest_list(const.apiKey[ind], const.apiSecret[ind], True)
            for contest in hq_contest['result']:
                if contest['name'].find("Тренировка HQ №") != -1 and const.authors.count(contest['preparedBy']) != 0:
                    contests.append(str(contest['id']))
                    apis[str(contest['id'])] = [const.apiKey[ind], const.apiSecret[ind]]
        #print('O VSTAL')
        return [contests, apis]

    #except:
     #   print('CF UPAL')


def take_contests():
    while True:
        temp = get_hq_contests()
        const.hq_contests = temp[0]
        const.apis = temp[1]
        const.hq_contests = sorted(const.hq_contests, key=cmp_to_key(comparator))
        time.sleep(30)

take_contests()

def get_all_rating():
    hq_rating = {}
    solved = {}
    upsolved = {}
    hq_rating_information = {}
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
    for item in hq_rating:
        user = item[0]
        hq_rating_information[user] = {}
        hq_rating_information[user]['solved'] = solved[user]
        hq_rating_information[user]['upsolved'] = upsolved[user]
        hq_rating_information[user]['rating'] = item[1]
    return hq_rating_information


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