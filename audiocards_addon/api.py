import requests
import pprint
import os

from typing import List, Dict
from dataclasses import dataclass, field

from . import logging_utils
from . import constants

logger = logging_utils.get_child_logger(__name__)

class DeckUpdateStatus:
    IN_PROGRESS = 'in_progress'
    ERROR = 'error'
    DONE = 'done'

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

@dataclass
class NewDeckSubset:
    deck_name: str
    deck_subset_name: str
    anki_deck_id: int
    anki_due_cards: bool
    anki_card_filter: str = None

@dataclass
class NewCardFormat:
    deck: str  # deck_id
    anki_note_type_id: int
    anki_card_ord: int
    template_name: str
    front_card_template: str
    back_card_template: str
    field_samples: List[Dict[str, str]]

class AudioCardsAPI:
    VOCABAI_APP_HOSTNAME = os.environ.get('VOCABAI_API_HOSTNAME', constants.VOCABAI_API_HOSTNAME)
    BASE_URL= f'https://{VOCABAI_APP_HOSTNAME}/audiocards-api/v1'
    UPDATE_MAX_CARD_NUM = 100

    def __init__(self, api_key):
        self.api_key = api_key
        logger.info(f'using AudioCards API hostname: {self.VOCABAI_APP_HOSTNAME}')

    def get_headers(self):
        return {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }

    def list_deck_subsets(self) -> List[DeckSubset]:
        url = f'{self.BASE_URL}/list_deck_subsets'
        response = requests.get(url, headers=self.get_headers(), timeout=constants.REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        results = []
        for deck_subset_data in data:
            results.append(DeckSubset(**deck_subset_data))
        return results

    def list_deck_card_formats(self, deck_id: str) -> List[DeckCardFormat]:
        url = f'{self.BASE_URL}/list_deck_card_formats/{deck_id}'
        response = requests.get(url, headers=self.get_headers(), timeout=constants.REQUEST_TIMEOUT_SECONDS)
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
            headers=self.get_headers(),
            timeout=constants.REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()

    def new_deck_subset(self, new_deck_subset: NewDeckSubset):
        url = f'{self.BASE_URL}/create_deck_subset'

        request_data = {
            'deck_name': new_deck_subset.deck_name,
            'name': new_deck_subset.deck_subset_name,
            'anki_deck_id': new_deck_subset.anki_deck_id,
            'anki_due_cards': new_deck_subset.anki_due_cards,
            'anki_static_cards': False,
            'anki_card_filter': new_deck_subset.anki_card_filter
        }

        response = requests.post(url,
            json=request_data,
            headers=self.get_headers(),
            timeout=constants.REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()

    def create_deck_card_format(self, new_card_format: NewCardFormat):
        url = f'{self.BASE_URL}/create_deck_card_format'

        request_data = {
            'deck': new_card_format.deck,
            'anki_note_type_id': new_card_format.anki_note_type_id,
            'anki_card_ord': new_card_format.anki_card_ord,
            'template_name': new_card_format.template_name,
            'front_card_template': new_card_format.front_card_template,
            'back_card_template': new_card_format.back_card_template,
            'field_samples': new_card_format.field_samples
        }

        logger.info(f'create_deck_card_format {pprint.pformat(request_data)}')

        response = requests.post(url,
            json=request_data,
            headers=self.get_headers(),
            timeout=constants.REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 201:
            logger.error(f'error creating deck card format: {response.status_code} {response.text}')
        response.raise_for_status()
        return response.json()

    def deck_update(self, status: str, update_version: int, error_message: str = None):
        url = f'{self.BASE_URL}/deck_update'
        request_data = {
            'status': status,
            'update_version': update_version
        }
        if error_message is not None:
            request_data['error_message'] = error_message
        logger.info(f'calling deck_update API with status={status}, update_version={update_version}')
        response = requests.patch(url,
            json=request_data,
            headers=self.get_headers(),
            timeout=constants.REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()


def validate_api_key(api_key: str):
    if not api_key:
        return False, 'API key is empty'
    hostname = AudioCardsAPI.VOCABAI_APP_HOSTNAME
    url = f'https://{hostname}/languagetools-api/v5/account'
    headers = {'Authorization': f'Api-Key {api_key}'}
    logger.info(f'validating API key against {url}')
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.warning(f'API key validation request failed: {e}')
        return False, f'Connection error: {e}'
    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            data = None
        logger.info(f'API key validation succeeded: {data}')
        if isinstance(data, dict):
            email = data.get('email') or data.get('user_email')
            account_type = data.get('type') or data.get('account_type')
            parts = [p for p in [email, account_type] if p]
            if parts:
                return True, 'API key is valid (' + ', '.join(parts) + ')'
        return True, 'API key is valid'
    if response.status_code in (401, 403):
        logger.info(f'API key rejected by server: {response.status_code}')
        return False, 'API key is invalid'
    logger.warning(f'API key validation got unexpected status {response.status_code}: {response.text}')
    return False, f'Unexpected response (HTTP {response.status_code})'