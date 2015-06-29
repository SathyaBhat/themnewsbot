import requests
import logging
import json
import os
import praw
import time

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('nbt')
with open('last_updated.txt', 'r') as f:
        last_updated_string=f.read()
        
f.close()
last_updated=int(last_updated_string)

BOT_KEY = '121846472:AAEF2t7PCTsCNL73xxcrLnGtAK3qAL_IBGo'
API_BASE = 'https://api.telegram.org/bot'



def get_updates():
    log.debug('Fetching telegram request')
    return json.loads(requests.get(API_BASE + BOT_KEY + '/getUpdates').text)


def get_latest_news():
    log.debug('fetching latest news')
    allposts=[]
    r = praw.Reddit(user_agent='Telegram Xiled Chippians Group')
    submissions = r.get_subreddit('programming').get_top(limit=5)      #Can change the subreddit or add more.
    for post in submissions:
        allposts.append(post.url)                                
    return allposts


def post_message(chat_id, text):
    log.debug('posting message')
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_BASE + BOT_KEY + '/sendMessage', data=payload)



if __name__ == '__main__':
    while (True):
        log.debug('Starting up')
        r = get_updates()
        if r['ok']:
            log.debug('Fetched sucessfully')
            for req in r['result']:
                if last_updated < req['update_id']:
                    n = get_latest_news()                                    #returns a list
                    #for i in n:
                        #post_message(req['message']['chat']['id'], i)
            last_updated = str(req['update_id'])
            with open('last_updated.txt', 'w') as f:
                f.write(last_updated)
        
            f.close()
            log.debug('last_updated: {0}'.format(last_updated))
