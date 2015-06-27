import requests
import logging
import json
import os

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('nbt')
last_updated = 0
BOT_KEY = os.environ['NBT_ACCESS_TOKEN']
API_BASE = 'https://api.telegram.org/bot'


def get_updates():
    log.debug('Fetching telegram request')
    return json.loads(requests.get(API_BASE + BOT_KEY + '/getUpdates').text)


def get_latest_news():
    log.debug('fetching latest news')
    return 'bloop bloop'


def post_message(chat_id, text):
    log.debug('posting message')
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_BASE + BOT_KEY + '/sendMessage', data=payload)


if __name__ == '__main__':
    log.debug('Starting up')
    r = get_updates()
    if r['ok']:
        log.debug('Fetched sucessfully')
        for req in r['result']:
            if last_updated < req['update_id']:
                n = get_latest_news()
                post_message(req['message']['chat']['id'], n)
        last_updated = req['update_id']
        log.debug('last_updated: {0}'.format(last_updated))
