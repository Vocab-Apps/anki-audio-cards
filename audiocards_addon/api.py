import requests

from typing import List
from dataclasses import dataclass, field

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



class AudioCardsAPI:
    BASE_URL= 'https://app.vocabai.dev/audiocards-api/v1'

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
