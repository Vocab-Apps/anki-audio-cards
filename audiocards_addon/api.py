import requests
import pprint

from typing import List
from dataclasses import dataclass, field

from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

@dataclass
class DeckSubset:
    id: str
    deck: str
    deck_name: str
    anki_deck_id: int
    name: str
    anki_due_cards: bool
    anki_card_filter: str
    anki_static_cards: bool

@dataclass
class DeckCardFormat:
    id: str
    anki_note_type_id: int
    anki_card_ord: int

# {
#     "id": str(card_format_2.id),
#     "anki_note_type_id": 445, 
#     "anki_card_ord":0
# }

# {
#     "id": str(deck_subset_2.id),
#     "deck": str(deck_1.id),
#     "deck_name": "Deck 1",
#     "anki_deck_id": 12345,
#     "name": "Subset 2",
#     "anki_due_cards": False,
#     "anki_card_filter": None,
#     "anki_static_cards": True
# }                

@dataclass
class NewDeckSubset:
    deck_name: str
    deck_subset_name: str
    anki_deck_id: int
    anki_due_cards: bool
    anki_card_filter: str = None

class AudioCardsAPI:
    BASE_URL= 'https://app.vocabai.dev/audiocards-api/v1'
    UPDATE_MAX_CARD_NUM = 100

    def __init__(self, api_key):
        self.api_key = api_key

    def get_headers(self):
        return {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }

    def list_deck_subsets(self) -> List[DeckSubset]:
        url = f'{self.BASE_URL}/list_deck_subsets'
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        data = response.json()
        results = []
        for deck_subset_data in data:
            results.append(DeckSubset(**deck_subset_data))
        return results

    def list_deck_card_formats(self, deck_id: str) -> List[DeckCardFormat]:
        url = f'{self.BASE_URL}/list_deck_card_formats/{deck_id}'
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        data = response.json()
        logger.debug(f'deck card format: {pprint.pformat(data)}')
        results = []
        for deck_card_format_data in data:
            results.append(DeckCardFormat(**deck_card_format_data))
        return results

    def create_update_cards(self, deck_subset_id: str, update_version: int, card_data_list: List[dict]):
        url = f'{self.BASE_URL}/create_update_cards'
        deck_info = {
            'deck_subset_id': deck_subset_id,
            'update_version': update_version
        }
        request_data = {
            'deck_info': deck_info,
            'cards': card_data_list
        }
        logger.info(f'calling create_update_cards API with {len(card_data_list)} cards')
        response = requests.post(url, 
            json=request_data, 
            headers=self.get_headers())
        response.raise_for_status()
        return response.json()