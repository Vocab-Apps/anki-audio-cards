import pprint
import datetime
from typing import List

from . import anki_interface
from . import api
from . import dialogs

from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

def get_api_instance():
    api_key = anki_interface.get_api_key()
    audiocards_api = api.AudioCardsAPI(api_key)
    return audiocards_api    

def sync_all_decks_with_audiocards():
    # first, query the audiocards api for the list of decks
    api_key = anki_interface.get_api_key()
    audiocards_api = api.AudioCardsAPI(api_key)

    logger.info(f'configured audiocards API with API key {api_key}')

    deck_subset_list: List[api.DeckSubset]  = audiocards_api.list_deck_subsets()
    logger.info(f'retrieved deck subset list: {pprint.pformat(deck_subset_list)}')

    deck_map = anki_interface.get_deck_map()

    for deck_subset in deck_subset_list:
        logger.info(f'syncing deck subset: {deck_subset}')
        anki_deck_id = deck_subset.anki_deck_id
        if anki_deck_id in deck_map:
            deck_name = deck_map[anki_deck_id]
            sync_deck(audiocards_api, deck_name, deck_subset)
        logger.info(f'finished syncing deck subset: {deck_subset}')

def sync_deck(audiocards_api, deck_name: str, deck_subset: api.DeckSubset):
    if deck_subset.anki_due_cards:
        # for now we only support syncing due cards
        logger.info('configured to sync due cards')

        # get the deck browser query
        browser_query = anki_interface.get_due_cards_browser_query(deck_name)

        # query existing card formats
        card_formats = audiocards_api.list_deck_card_formats(deck_subset.deck)
        card_format_map = anki_interface.get_card_format_map(card_formats)

        # do we have any unknown card formats?
        for card_format in anki_interface.iterate_unkown_card_formats(browser_query, card_format_map):
            logger.info(f'unknown card format: {card_format}, need to create the format')
            front_template, back_template = anki_interface.get_card_templates(card_format)
            field_samples = anki_interface.get_card_samples(deck_name, card_format)
            # logger.info(f'front template: {front_template}, back template: {back_template}')
            new_card_format: api.NewCardFormat = api.NewCardFormat(
                deck=deck_subset.deck,
                anki_note_type_id=card_format.note_type_id,
                anki_card_ord=card_format.card_ord,
                front_card_template=front_template,
                back_card_template=back_template,
                field_samples=field_samples
            )
            logger.info(f'creating new card format: {pprint.pformat(new_card_format)}')
            response = audiocards_api.create_deck_card_format(new_card_format)
            logger.info(f'created card format: {response}')

        # now, refresh the card formats
        card_formats = audiocards_api.list_deck_card_formats(deck_subset.deck)
        card_format_map = anki_interface.get_card_format_map(card_formats)        

        update_version = int(datetime.datetime.now().timestamp())

        # iterate over due cards in slices
        for card_data_list in anki_interface.iterate_due_cards_slices(deck_name, card_format_map, api.AudioCardsAPI.UPDATE_MAX_CARD_NUM):
            response = audiocards_api.create_update_cards(deck_subset.id, update_version, card_data_list)
            

def register_new_deck():
    logger.info('registering new deck')
    deck_list: List[anki_interface.Deck] = anki_interface.get_deck_list()
    result = dialogs.create_deck_subset(deck_list)
    if result != None:
        logger.info(f'create deck subset result: {pprint.pformat(result)}')
        audiocards_api = get_api_instance()
        try:
            query_result = audiocards_api.new_deck_subset(result)
            logger.info(f'created deck subset: {query_result}')
        except Exception as e:
            logger.error(f'error creating deck subset: {e}')