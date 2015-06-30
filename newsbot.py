import requests
import logging
import json
import os
import praw

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('nbt')

try:
    with open('last_updated.txt', 'r') as f:
        try:
            last_updated = int(f.read())
        except ValueError:
            last_updated = 0
    f.close()
except FileNotFoundError:
    last_updated = 0
    
skip_list = []

BOT_KEY = os.environ['NBT_ACCESS_TOKEN']
API_BASE = 'https://api.telegram.org/bot'


def summarize(url):
    log.info('Not yet implemented!')
    return url


def get_updates():
    log.debug('Checking for requests')
    return json.loads(requests.get(API_BASE + BOT_KEY + '/getUpdates').text)


def get_latest_news():
    log.debug('Fetching news from reddit')
    r = praw.Reddit(user_agent='Telegram Xiled Chippians Group')
    # Can change the subreddit or add more.
    submissions = r.get_subreddit('programming').get_top(limit=5)
    submisssion_content = ''
    for post in submissions:
        submisssion_content += summarize(post.url) + '\n'
    return submisssion_content


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
                    chat_sender_id = req['message']['chat']['id']
                    chat_text = req['message']['text']
                    log.debug('Chat text received: {0}'.format(chat_text))
                    if chat_text == '/stop':
                        log.debug('Added {0} to skip list'.format(chat_sender_id))
                        skip_list.append(chat_sender_id)
                    if chat_sender_id not in skip_list:
                        summarized_news = get_latest_news()
                        post_message(chat_sender_id, summarized_news)
                        log.debug(
                            "Posting {0} to {1}".format(summarized_news, chat_sender_id))
                    last_updated = req['update_id']
                    with open('last_updated.txt', 'w') as f:
                        f.write(str(last_updated))
                        log.debug(
                            'Updated last_updated to {0}'.format(last_updated))
                    f.close()
