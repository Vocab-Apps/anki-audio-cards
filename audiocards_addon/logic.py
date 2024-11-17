import pprint
from typing import List
from . import anki_interface
from . import api

def sync_all_decks_with_audiocards():
    # first, query the audiocards api for the list of decks
    api_key = anki_interface.get_api_key()
    audiocards_api = api.AudioCardsAPI(api_key)
    deck_subset_list: List[api.DeckSubset]  = audiocards_api.list_deck_subsets()

    deck_map = anki_interface.get_deck_map()

    for deck_subset in deck_subset_list:
        anki_deck_id = deck_subset.anki_deck_id
        if anki_deck_id in deck_map:
            deck_name = deck_map[anki_deck_id]
            sync_deck(audiocards_api, deck_name, deck_subset)

def sync_deck(audiocards_api, deck_name: str, deck_subset: api.DeckSubset):
    if deck_subset.anki_due_cards:
        # for now we only support syncing due cards
        
        # query existing card formats
        card_formats = audiocards_api.list_deck_card_formats(deck_subset.deck)

        # iterate over due cards
        for card_data in anki_interface.iterate_due_cards(deck_name, card_formats):
            pprint.pprint(card_data)