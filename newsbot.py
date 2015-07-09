import requests
import logging
import json
import os
import praw
import re

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('nbt')
ERR_NO_SOURCE = 'No sources defined! Set a source using /source list, of, sub, reddits'

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
sources_dict = {}

BOT_KEY = os.environ['NBT_ACCESS_TOKEN']
API_BASE = 'https://api.telegram.org/bot'


def summarize(url):
    log.info('Not yet implemented!')
    return url


def clean_up_subreddits(sub_reddits):
    log.debug('Got subreddits to clean: {0}'.format(sub_reddits))
    return sub_reddits.strip().replace(" ", "").replace(',', '+')


def get_updates():
    log.debug('Checking for requests')
    return json.loads(requests.get(API_BASE + BOT_KEY + '/getUpdates', params={'offset': last_updated+1}).text)


def get_latest_news(sub_reddits):
    log.debug('Fetching news from reddit')
    r = praw.Reddit(user_agent='Telegram Xiled Chippians Group')
    # Can change the subreddit or add more.
    sub_reddits = clean_up_subreddits(sub_reddits)
    log.debug('Fetching subreddits: {0}'.format(sub_reddits))
    submissions = r.get_subreddit(sub_reddits).get_top(limit=5)
    submisssion_content = ''
    for post in submissions:
        submisssion_content += summarize(post.url) + '\n'
    return submisssion_content


def post_message(chat_id, text):
    log.debug('posting message to {0}'.format(chat_id))
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_BASE + BOT_KEY + '/sendMessage', data=payload)


if __name__ == '__main__':
    log.debug('Starting up')
    log.debug('Last updated id: {0}'.format(last_updated))
    while (True):
        r = get_updates()
        if r['ok']:
            for req in r['result']:
                chat_sender_id = req['message']['chat']['id']
                chat_text = req['message']['text']
                log.debug('Chat text received: {0}'.format(chat_text))
                r = re.search('(source+)(.*)', chat_text)

                if (r is not None and r.group(1) == 'source'):
                    sources_dict[chat_sender_id] = r.group(2)
                    log.debug('Sources set for {0} to {1}'.format(sources_dict[chat_sender_id], r.group(2)))
                    last_updated = req['update_id']
                if chat_text == '/stop':
                    log.debug('Added {0} to skip list'.format(chat_sender_id))
                    skip_list.append(chat_sender_id)
                    last_updated = req['update_id']
                if chat_text =='/start':
                    helptext=
                    '''
                        Hi! This is a News Bot which fetches news from subreddits\nUse "/source" to select a subreddit source.\n
                        Example "/source programming,games" fetches news from r/programming, r/games\n
                        Use "/stop" to stop the bot
                    '''
                    post_message(chat_sender_id, helptext)
                    last_updated = req['update_id']

                  
                if (chat_text == '/fetch' and (chat_sender_id not in skip_list)):
                    try:
                        sub_reddits = sources_dict[chat_sender_id]
                    except KeyError:
                        post_message(chat_sender_id, ERR_NO_SOURCE)
                    else:
                        summarized_news = get_latest_news(sources_dict[chat_sender_id])
                        post_message(chat_sender_id, summarized_news)
                        log.debug(
                            "Posting {0} to {1}".format(summarized_news, chat_sender_id))
                    last_updated = req['update_id']
                with open('last_updated.txt', 'w') as f:
                    f.write(str(last_updated))
                    log.debug(
                        'Updated last_updated to {0}'.format(last_updated))
                f.close()
