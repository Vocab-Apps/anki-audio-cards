import pprint
import time
import json
import datetime
import requests

import aqt
# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

import anki.consts

from . import logging_utils
logger = logging_utils.get_child_logger(__name__)

from . import logic

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def testFunction() -> None:
    # get the number of cards in the current collection, which is stored in
    # the main window
    cardCount = mw.col.cardCount()
    # show a message box
    print(f'card count: {cardCount}')

    # note id: 1553256458477
    wanted_card_id = 1553256458488

    card = mw.col.get_card(wanted_card_id)
    print(f"""
card id: {card.id}
deck id: {card.did}
queue: {card.queue}
type: {card.type}
ivl: {card.ivl}
due: {card.due}
odue: {card.odue}
    """)    

    # # ids = mw.col.find_cards("deck:Hanzi is:due")
    # # pprint.pprint(ids)
    # for id in ids:
    #     if id == wanted_card_id:
    #         card = mw.col.get_card(id)
    #         print(f"""
    # card id: {card.id}
    # deck id: {card.did}
    # due: {card.due}
    # odue: {card.odue}
    #         """)
        # pprint.pprint(card)
    # showInfo("Card count: %d" % cardCount)

def get_card_type_str(card_type):
    if card_type == anki.consts.CARD_TYPE_NEW:
        return "new"
    elif card_type == anki.consts.CARD_TYPE_REV:
        return "review"
    elif card_type == anki.consts.CARD_TYPE_LRN:
        return "learn"
    elif card_type == anki.consts.CARD_TYPE_RELEARNING:
        return "relearning"
    else:
        return "unknown"

def get_card_queue_str(card_queue: anki.consts.CardQueue) -> str:
    if card_queue == anki.consts.QUEUE_TYPE_NEW:
        return "new"
    elif card_queue == anki.consts.QUEUE_TYPE_REV:
        return "review"
    elif card_queue == anki.consts.QUEUE_TYPE_LRN:
        return "learn"
    elif card_queue == anki.consts.QUEUE_TYPE_MANUALLY_BURIED:
        return "manually buried"
    elif card_queue == anki.consts.QUEUE_TYPE_SIBLING_BURIED:
        return "sibling buried"
    elif card_queue == anki.consts.QUEUE_TYPE_SUSPENDED:
        return "suspended"
    elif card_queue == anki.consts.QUEUE_TYPE_DAY_LEARN_RELEARN:
        return "day learn relearn"
    elif card_queue == anki.consts.QUEUE_TYPE_PREVIEW:
        return "preview"
    else:
        return "unknown"


def print_card_data(card_id):
    card = mw.col.get_card(card_id)
    note = card.note()
    print(f"""
=================================
queue: {card.queue} / {get_card_queue_str(card.queue)}
type: {card.type} / {get_card_type_str(card.type)}
=================================
card id: {card.id}
deck id: {card.did}
note id: {card.nid}
note type id: {note.mid}
ord: {card.ord}
ivl: {card.ivl}
due: {card.due}
odue: {card.odue}
odid: {card.odid}
    """)    

    # 1729051919
    # 1700000000
    if card.due > 1700000000:
        # epoch
        # compute number of seconds compared to now
        now = time.time()
        seconds = card.due - now
        print(f"due in {seconds} seconds")

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
        scheduler_timing_today = mw.col._backend.sched_timing_today()
        days_remaining = card.due - scheduler_timing_today.days_elapsed
        due_time_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days_remaining)
        # print(f"scheduler today: type: {type(scheduler_today)} {scheduler_today}")
        return due_time_dt
    raise Exception(f"unknown card type: {card.type}")


def get_card_reviews(card_id):
    reviews = mw.col.get_review_logs(card_id)
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

def get_required_card_data(card_id):
    card = mw.col.get_card(card_id)
    due_time_dt = get_card_due_time_dt(card)
    due_time_iso = due_time_dt.isoformat()
    reviews = get_card_reviews(card_id)
    note = card.note()
    # fields = note._fmap

    fields_dict = dict(zip(note.keys(), note.values()))
    return {
        'anki_card_id': card.id,
        'fields': fields_dict,
        'card_type': card.type,
        'due_time': due_time_iso,
        'review_times': reviews['review_times'],
        'review_ratings': reviews['review_ratings']
    }

def export_required_card_data_fn(browser):
    def export_required_card_data():
        card_id_list = browser.selectedCards()
        card_data_list = []
        for card_id in card_id_list:
            card_data = get_required_card_data(card_id)
            card_data_list.append(card_data)
        
        target_filename = '/home/luc/temp/anki_audiocards_data.json'
        with open(target_filename, 'w') as f:
            json.dump(card_data_list, f, indent=4)
        
    return export_required_card_data

def get_card_data_fn(browser):
    def card_data():
        #card = browser.card
        card_id_list = browser.selectedCards()
        card_id = card_id_list[0]
        print_card_data(card_id)
        
    return card_data

def build_vocabai_audiocards_card_data(card_id, card_format_id):
    card_data = get_required_card_data(card_id)
    card_data['card_format'] = card_format_id
    return card_data

def sync_due_cards_with_audiocards():
    # config = aqt.mw.addonManager.getConfig(__name__)
    config = mw.addonManager.getConfig('anki-audio-cards')
    vocabai_api_key = config['api_key']
    
    start_time = time.time()  # Record start time

    print(f'sync_with_audiocards, api_key: {vocabai_api_key}')
    card_ids = mw.col.find_cards("deck:Mandarin is:due")

    update_version = int(datetime.datetime.now().timestamp())
    deck_subset_id = 'ae9c9e15-69a5-451c-915a-1adfb8c9d696'

    card_format_id = 'b43ebbda-ad98-40e1-8e4b-67f28aa30a78'
    deck_info = {
        'deck_subset_id': deck_subset_id,
        'update_version': update_version
    }


    max_num_cards = 100

    for i in range(0, len(card_ids), max_num_cards):
        card_ids_slice = card_ids[i:i + max_num_cards]
        processed_card_data_list = [build_vocabai_audiocards_card_data(card_id, card_format_id) for card_id in card_ids_slice]

        request_data = {
            'deck_info': deck_info,
            'cards': processed_card_data_list
        }

        # url = reverse("audiocards-api:create_update_cards")
        url = 'https://app.vocabai.dev/audiocards-api/v1/create_update_cards'
        print(f'starting post request on {url}')
        pprint.pprint(request_data)
        response = requests.post(url, 
            json=request_data, 
            headers={
                'Authorization': f'Api-Key {vocabai_api_key}',
                'Content-Type': 'application/json'
            })
        print(f'status code: {response.status_code}')
        if response.status_code != 200:
            print(f'error: {response.content}')

    end_time = time.time()  # Record end time
    print(f"Time taken: {end_time - start_time} seconds")

def sync_due_cards_fn(browser):
    def sync_due_cards():
        #card = browser.card
        # card_id_list = browser.selectedCards()
        sync_due_cards_with_audiocards()
    return sync_due_cards

def sync_all_decks_fn(browser):
    def sync_all_decks():
        logic.sync_all_decks_with_audiocards()
    return sync_all_decks

def sync_all_decks_action():
    logger.info('starting to sync all decks')
    logic.sync_all_decks_with_audiocards()

def register_new_deck():
    logger.info('registering new deck')
    logic.register_new_deck()


def browerMenusInit(browser: aqt.browser.Browser):
    menu = aqt.qt.QMenu('AudioCards', browser.form.menubar)
    browser.form.menubar.addMenu(menu)

    action = aqt.qt.QAction(f'card debug info', browser)
    action.triggered.connect(get_card_data_fn(browser))
    menu.addAction(action)

    action = aqt.qt.QAction(f'export card data', browser)
    action.triggered.connect(export_required_card_data_fn(browser))
    menu.addAction(action)

    action = aqt.qt.QAction(f'sync with audiocards', browser)
    action.triggered.connect(sync_due_cards_fn(browser))
    menu.addAction(action)

    action = aqt.qt.QAction(f'sync all decks with audiocards', browser)
    action.triggered.connect(sync_all_decks_fn(browser))
    menu.addAction(action)    


def setup_gui():
    # browser menus
    aqt.gui_hooks.browser_menus_did_init.append(browerMenusInit)

    # tools menu
    action = aqt.qt.QAction(f'AudioCards: Sync All Decks', aqt.mw)
    action.triggered.connect(sync_all_decks_action)
    aqt.mw.form.menuTools.addAction(action)    

    action = aqt.qt.QAction(f'AudioCards: Register New Deck', aqt.mw)
    action.triggered.connect(register_new_deck)
    aqt.mw.form.menuTools.addAction(action)        