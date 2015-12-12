__author__ = 'Sathyajith'

import re
import time
import json
import requests

from states import States, log
from constants import *
from reddit import get_latest_news

def get_updates(last_updated):
    log.debug('Checking for requests, last updated passed is: {}'.format(last_updated))
    time.sleep(UDPATE_PERIOD)
    return json.loads(requests.get(API_BASE + BOT_KEY + '/getUpdates', params={'offset': last_updated+1}).text)

def post_message(chat_id, text):
    log.debug('posting message to {0}'.format(chat_id))
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_BASE + BOT_KEY + '/sendMessage', data=payload)


def handle_incoming_messages(last_updated):
    r = get_updates(last_updated)
    if r['ok']:
        for req in r['result']:
            chat_sender_id = req['message']['chat']['id']
            try:
                chat_text = req['message']['text']
            except KeyError:
                chat_text = ''
                log.debug('Looks like no chat text was detected... moving on')
            log.debug('Chat text received: {0}'.format(chat_text))
            r = re.search('(source+)(.*)', chat_text)

            if (r is not None and r.group(1) == 'source'):
                if r.group(2):
                    sources_dict[chat_sender_id] = r.group(2)
                    log.debug('Sources set for {0} to {1}'.format(sources_dict[chat_sender_id], r.group(2)))
                    post_message(chat_sender_id, 'Sources set as {0}!'.format(r.group(2)))
                else:
                    post_message(chat_sender_id, 'We need a comma separated list of subreddits! No subreddit, no news :-(')

            if chat_text == '/stop':
                log.debug('Added {0} to skip list'.format(chat_sender_id))
                skip_list.append(chat_sender_id)
                post_message(chat_sender_id, "Ok, we won't send you any more messages.")

            if chat_text in ('/start', '/help'):
                helptext = '''
                    Hi! This is a News Bot which fetches news from subreddits\nUse "/source" to select a subreddit source.\n
                    Example "/source programming,games" fetches news from r/programming, r/games\n
                    Use "/stop" to stop the bot
                '''
                post_message(chat_sender_id, helptext)

            if (chat_text == '/fetch' and (chat_sender_id not in skip_list)):
                post_message(chat_sender_id, 'Hang on, fetching your news..')
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
                States.last_updated = last_updated
                log.debug(
                    'Updated last_updated to {0}'.format(last_updated))
            f.close()

