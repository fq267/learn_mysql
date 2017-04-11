import time
import random
import urllib.request

url = 'http://vgd.no/musikk-tv-og-film/jazz'

file = open('/home/fanq/Workspace/learn_mysql/user_agent.log', 'r')
theFirstFiveWordOfUserAgent = ''
counter = 0
for line in file:
    counter = counter + 1
    userAgent = line.strip()
    if (theFirstFiveWordOfUserAgent == userAgent[:5]):
        print(userAgent, 'skiped.')
        print('\n')
    else:
        theFirstFiveWordOfUserAgent = userAgent[:5]
        headers = {'User-agent': userAgent}

        req = urllib.request.Request(url, headers=headers)
        try:
            f = urllib.request.urlopen(req)
            print(userAgent, 'works well.')
        except urllib.error.HTTPError as e:
            print(userAgent, e)
        # except TimeoutError as e:
        #     print(userAgent, e)
        print('\n')
        waitTime = random.randint(1, 10)
        time.sleep(waitTime)
file.close()
