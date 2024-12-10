import datetime
import time

import anki
import aqt

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
    card = aqt.mw.col.get_card(card_id)
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

def get_required_card_data(card_id):
    card = aqt.mw.col.get_card(card_id)
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

