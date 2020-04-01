import hashlib
import time
from pip._vendor import requests
import const

apiKey = const.apiKey
apiSecret = const.apiSecret

count_response = 0
def get_cf_response(url):
    global count_response
    if count_response==5:
        count_response = 0
        time.sleep(2)
    r = requests.get(url)
    count_response += 1
    return r.json()


def get_codeforces_contest_stadings(contestId, showUnofficial=False):
    if showUnofficial:
        showUnofficial = 'true'
    else:
        showUnofficial = 'false'

    t = int(time.time())
    s = bytes("hqhqhq/contest.standings?apiKey="+apiKey+"&contestId="+str(contestId)+"&showUnofficial="+showUnofficial+"&time="+str(t)+"#"+apiSecret, 'utf-8')
    h = hashlib.sha512(s).hexdigest()

    url = "http://codeforces.com/api/contest.standings?apiKey="+apiKey+"&contestId="+str(contestId)+"&showUnofficial="+showUnofficial+"&time="+str(t)+"&apiSig=hqhqhq"+h
    #print(url)
    return get_cf_response(url)


def get_codeforces_contest_status(contestId):
    t = int(time.time())
    s = bytes("hqhqhq/contest.status?apiKey="+apiKey+"&contestId="+str(contestId)+"&time="+str(t)+"#"+apiSecret, 'utf-8')
    h = hashlib.sha512(s).hexdigest()

    url = "http://codeforces.com/api/contest.status?apiKey=" + apiKey + "&contestId=" + str(
        contestId) + "&time=" + str(t) + "&apiSig=hqhqhq" + h
    #print(url)
    return get_cf_response(url)


def get_codeforces_contest_list(gym=False):
    if gym:
        gym = 'true'
    else:
        gym = 'false'

    t = int(time.time())
    s = bytes(
        "hqhqhq/contest.list?apiKey=" + apiKey + "&gym=" + gym +  "&time=" + str(t) + "#" + apiSecret,
        'utf-8')
    h = hashlib.sha512(s).hexdigest()

    url = "http://codeforces.com/api/contest.list?apiKey=" + apiKey + "&gym=" + gym + "&time=" + str(t) + "&apiSig=hqhqhq" + h
    return get_cf_response(url)


def get_contestName(contestId):
    try:
        standings = get_codeforces_contest_stadings(contestId)
        return standings['result']['contest']['name']
    except:
        return None


#print(get_codeforces_contest_list(True))
#print(get_codeforces_contest_stadings(273749, True))
#print(get_codeforces_contest_status(273749))