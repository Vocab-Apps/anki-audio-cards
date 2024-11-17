import sys
import os
import pprint

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import audiocards_addon.api

api_key = os.environ.get('ANKI_AUDIO_CARDS_API_KEY')
api = audiocards_addon.api.AudioCardsAPI(api_key)
deck_subset_list = api.list_deck_subsets()
pprint.pprint(deck_subset_list)
