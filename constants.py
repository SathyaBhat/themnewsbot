__author__ = 'Sathyajith'

import os
ERR_NO_SOURCE = 'No sources defined! Set a source using /source list, of, sub, reddits'
skip_list = []
sources_dict = {}

BOT_KEY = os.environ['NBT_ACCESS_TOKEN']
API_BASE = 'https://api.telegram.org/bot'
UDPATE_PERIOD = 6