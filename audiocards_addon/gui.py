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
from aqt.operations import QueryOp
# import all of the Qt GUI library
from aqt.qt import *

import anki.consts

from . import logging_utils
logger = logging_utils.get_child_logger(__name__)

from . import logic
from . import debug_data


def sync_all_decks_fn(browser):
    def sync_all_decks():
        logic.sync_all_decks_with_audiocards()
    return sync_all_decks

def sync_all_decks_action():
    logger.info('starting to sync all decks')
    op = QueryOp(
        parent=mw,
        op=lambda col: logic.sync_all_decks_with_audiocards(),
        success=lambda result: None,
    )
    op.with_progress(label='Syncing all decks with AudioCards...').run_in_background()

def register_new_deck():
    logger.info('registering new deck')
    new_deck_subset = logic.get_new_deck_subset_from_dialog()
    if new_deck_subset is None:
        return

    op = QueryOp(
        parent=mw,
        op=lambda col: logic.create_deck_subset(new_deck_subset),
        success=lambda result: None,
    )
    op.with_progress(label='Registering new deck with AudioCards...').run_in_background()


def browerMenusInit(browser: aqt.browser.Browser):
    menu = aqt.qt.QMenu('AudioCards', browser.form.menubar)
    browser.form.menubar.addMenu(menu)

    action = aqt.qt.QAction(f'card debug info', browser)
    action.triggered.connect(debug_data.get_card_data_fn(browser))
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