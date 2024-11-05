import pprint
import time
import json
import datetime

import aqt
# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

import anki.consts

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
    print(f"""
=================================
queue: {card.queue} / {get_card_queue_str(card.queue)}
type: {card.type} / {get_card_type_str(card.type)}
=================================
card id: {card.id}
deck id: {card.did}
note id: {card.nid}
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

def browerMenusInit(browser: aqt.browser.Browser):
    menu = aqt.qt.QMenu('AudioCards', browser.form.menubar)
    browser.form.menubar.addMenu(menu)

    action = aqt.qt.QAction(f'card debug info', browser)
    action.triggered.connect(get_card_data_fn(browser))
    menu.addAction(action)

    action = aqt.qt.QAction(f'export card data', browser)
    action.triggered.connect(export_required_card_data_fn(browser))
    menu.addAction(action)

# create a new menu item, "test"
action = QAction("AudioCards Test", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

aqt.gui_hooks.browser_menus_did_init.append(browerMenusInit)