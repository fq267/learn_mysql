import time
import random
import urllib.request
import argparse
import logging

import sys


def find_user_agent(args):
    if args.path:
        path = args.path
    else:
        path = '/home/fanq/Workspace/learn_mysql/user_agent.log'
    url = args.link
    begin = args.begin

    theFirstFiveWordOfUserAgent = ''
    counter = 0
    file = open(path, 'r')
    for line in file:
        counter += 1
        if counter > begin:
            userAgent = line.strip()
            if theFirstFiveWordOfUserAgent == userAgent[:5]:
                pass
            else:
                theFirstFiveWordOfUserAgent = userAgent[:5]
                headers = {'User-agent': userAgent}

                req = urllib.request.Request(url, headers=headers)
                try:
                    urllib.request.urlopen(req)
                    print(counter, userAgent, 'works well.')
                except urllib.error.HTTPError as e:
                    print(counter, userAgent, e)
                except TimeoutError as e:
                    print(counter, userAgent, e)
                waitTime = random.randint(1, 5)
                time.sleep(waitTime)
    file.close()


if __name__ == '__main__':
    description = 'Download a given url with different userAgent, return ' \
                  'those if they can download the url successfully.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-p', '--path', help='the path of the file which '
                                             'contains lots of userAgents')
    parser.add_argument('-l', '--link', help='url you want to download')
    parser.add_argument('-b', '--begin',
                        help='which line in the file you want begin with.',
                        default=0, type=int)
    args = parser.parse_args()

    if not args.link:
        logging.Logger.info(
            "the following arguments are required: -l")
        sys.exit()
    find_user_agent(args)
