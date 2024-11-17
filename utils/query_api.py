import sys
import os
import pprint

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import audiocards_addon.api

api_key = os.environ.get('ANKI_AUDIO_CARDS_API_KEY')
api = audiocards_addon.api.AudioCardsAPI(api_key)

# query_deck_subset_list = False
deck_subset_list = api.list_deck_subsets()
pprint.pprint(deck_subset_list)
for deck_subset in deck_subset_list:
    deck_id = deck_subset.deck
    deck_card_formats = api.list_deck_card_formats(deck_id)
    pprint.pprint(deck_card_formats)

