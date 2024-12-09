import datetime
import random
from dataclasses import dataclass
from typing import List, Dict

import aqt
import anki

from . import api
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

@dataclass
class Deck:
    id: int
    name: str

@dataclass(frozen=True) # required for hashing
class CardFormat:
    note_type_id: int
    card_ord: int

def get_api_key():
    config = aqt.mw.addonManager.getConfig('anki-audio-cards')
    vocabai_api_key = config['api_key']
    return vocabai_api_key

def get_deck_list() -> List[Deck]:
    deck_list = aqt.mw.col.decks.all_names_and_ids()
    decks = []
    for deck in deck_list:
        deck = Deck(id=deck.id, name=deck.name)
        decks.append(deck)
    return decks

def get_deck_map():
    deck_list = aqt.mw.col.decks.all_names_and_ids()
    deck_map = {}
    for deck in deck_list:
        deck_map[deck.id] = deck.name
    return deck_map

def get_card_due_time_dt(card):
    if card.type == anki.consts.CARD_TYPE_NEW:
        # probably need to create due time
        return None
    elif card.type in [anki.consts.CARD_TYPE_LRN, anki.consts.CARD_TYPE_RELEARNING]:
        due_time_dt = datetime.datetime.fromtimestamp(card.due)
        return due_time_dt
    elif card.type == anki.consts.CARD_TYPE_REV:
        # days since the colection creation time
        # due date calculation: https://github.com/ankitects/anki/blob/main/rslib/src/stats/card.rs#L93
        scheduler_timing_today = aqt.mw.col._backend.sched_timing_today()
        days_remaining = card.due - scheduler_timing_today.days_elapsed
        due_time_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days_remaining)
        # print(f"scheduler today: type: {type(scheduler_today)} {scheduler_today}")
        return due_time_dt
    raise Exception(f"unknown card type: {card.type}")


def get_card_reviews(card_id):
    reviews = aqt.mw.col.get_review_logs(card_id)
    review_times = []
    review_ratings = []
    for review in reviews:
        if review.button_chosen != 0:
            review_time = datetime.datetime.fromtimestamp(review.time)
            review_times.append(review_time.isoformat())
            review_ratings.append(review.button_chosen)
    # pprint.pprint(reviews)
    # reverse arrays
    review_times.reverse()
    review_ratings.reverse()
    return {
        'review_times': review_times,
        'review_ratings': review_ratings
    }

def build_card_data(card_id, card_format_map):
    card = aqt.mw.col.get_card(card_id)
    due_time_dt = get_card_due_time_dt(card)
    due_time_iso = due_time_dt.isoformat()
    reviews = get_card_reviews(card_id)
    note = card.note()
    # fields = note._fmap

    card_format = CardFormat(note_type_id=note.mid, card_ord=card.ord)
    card_format_id = card_format_map[card_format]

    fields_dict = dict(zip(note.keys(), note.values()))
    return {
        'anki_card_id': card.id,
        'card_format': card_format_id,
        'fields': fields_dict,
        'card_type': card.type,
        'due_time': due_time_iso,
        'review_times': reviews['review_times'],
        'review_ratings': reviews['review_ratings']
    }

def get_card_format_map(card_formats: List[api.DeckCardFormat]) -> dict:
    card_format_map = {}
    for card_format in card_formats:
        card_format_map[CardFormat(
            note_type_id=card_format.anki_note_type_id, 
            card_ord=card_format.anki_card_ord)] = card_format.id
    return card_format_map

def get_due_cards_browser_query(deck_name: str):
    return f"deck:{deck_name} is:due"

def iterate_due_cards(deck_name: str, card_format_map):

    card_ids = aqt.mw.col.find_cards(f"deck:{deck_name} is:due")
    for card_id in card_ids:
        card_data = build_card_data(card_id, card_format_map)
        yield card_data


def iterate_due_cards_slices(deck_name:str, card_format_map, max_items):

    card_ids = aqt.mw.col.find_cards(f"deck:{deck_name} is:due")
    for i in range(0, len(card_ids), max_items):
        card_ids_slice = card_ids[i:i + max_items]
        card_data_list = []
        for card_id in card_ids_slice:
            card_data = build_card_data(card_id, card_format_map)
            card_data_list.append(card_data)

        yield card_data_list

def iterate_unkown_card_formats(browser_query: str, card_format_map):
    reported_unknown_format_map = {}

    logger.info(f'iterating unknown card formats for query: {browser_query}')
    card_ids = aqt.mw.col.find_cards(browser_query)
    for card_id in card_ids:
        card = aqt.mw.col.get_card(card_id)
        note = card.note()
        card_format = CardFormat(note_type_id=note.mid, card_ord=card.ord)
        if card_format not in card_format_map:
            # found unknown card format
            if card_format not in reported_unknown_format_map:
                logger.info(f'unknown card format: {card_format}')
                reported_unknown_format_map[card_format] = True
                yield card_format

def get_card_templates(card_format: CardFormat):
    note_type = aqt.mw.col.models.get(card_format.note_type_id)
    template = note_type['tmpls'][card_format.card_ord]
    return template['qfmt'], template['afmt']

def get_card_samples(deck_name: str, card_format: CardFormat) -> Dict[str, List[str]]:
    browser_query = f'mid:{card_format.note_type_id} deck:"{deck_name}"'
    card_ids = aqt.mw.col.find_cards(browser_query)
    max_samples = 100
    selected_card_ids = random.sample(card_ids, min(max_samples, len(card_ids)))

    field_samples = {}
    for card_id in selected_card_ids:
        card = aqt.mw.col.get_card(card_id)
        note = card.note()
        for field_name in note.keys():
            if field_name not in field_samples:
                field_samples[field_name] = []
            field_samples[field_name].append(note[field_name])

    return field_samples


