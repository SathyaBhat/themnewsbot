import requests
import logging
import json
import os
import praw

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('nbt')

with open('last_updated.txt', 'r') as f:
    try:
        last_updated = int(f.read())
    except ValueError:
        last_updated = 0
f.close()


BOT_KEY = os.environ['NBT_ACCESS_TOKEN']
API_BASE = 'https://api.telegram.org/bot'


def get_updates():
    log.debug('Checking for requests')
    return json.loads(requests.get(API_BASE + BOT_KEY + '/getUpdates').text)


def get_latest_news():
    log.debug('Fetching news from reddit')
    allposts = []
    r = praw.Reddit(user_agent='Telegram Xiled Chippians Group')
    # Can change the subreddit or add more.
    submissions = r.get_subreddit('programming').get_top(limit=5)
    for post in submissions:
        allposts.append(post.url)
    return allposts


def post_message(chat_id, text):
    log.debug('posting messaget to {0}'.format(chat_id))
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_BASE + BOT_KEY + '/sendMessage', data=payload)


if __name__ == '__main__':
    log.debug('Starting up')
    log.debug('Last updated id: {0}'.format(last_updated))
    while (True):
        r = get_updates()
        if r['ok']:
            for req in r['result']:
                if req['update_id'] > last_updated:
                    n = get_latest_news()  # returns a list
                    for i in n:
                        post_message(req['message']['chat']['id'], i)
                        log.debug("Posting...")
                    last_updated = req['update_id']
                    with open('last_updated.txt', 'w') as f:
                        f.write(str(last_updated))
                        log.debug(
                            'Updated last_updated to {0}'.format(last_updated))
                    f.close()
