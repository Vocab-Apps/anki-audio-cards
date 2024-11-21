import pprint
import datetime
from typing import List

from . import anki_interface
from . import api

from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

def sync_all_decks_with_audiocards():
    # first, query the audiocards api for the list of decks
    api_key = anki_interface.get_api_key()
    audiocards_api = api.AudioCardsAPI(api_key)

    logger.info(f'configured audiocards API with API key {api_key}')

    deck_subset_list: List[api.DeckSubset]  = audiocards_api.list_deck_subsets()
    logger.info(f'retrieved deck subset list: {pprint.pformat(deck_subset_list)}')

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

        update_version = int(datetime.datetime.now().timestamp())

        # iterate over due cards in slices
        for card_data_list in anki_interface.iterate_due_cards_slices(deck_name, card_formats, api.AudioCardsAPI.UPDATE_MAX_CARD_NUM):
            response = audiocards_api.create_update_cards(deck_subset.id, update_version, card_data_list)
            