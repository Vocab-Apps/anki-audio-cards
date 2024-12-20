import aqt
from aqt import (QDialog, QComboBox, QVBoxLayout, QHBoxLayout, 
                           QRadioButton, QLineEdit, QLabel, QPushButton, 
                           QButtonGroup)

from . import logging_utils
from . import api

from typing import List, Optional
from . import anki_interface
from . import api

logger = logging_utils.get_child_logger(__name__)

class CreateDeckSubsetDialog(QDialog):
    def __init__(self, decks: List[anki_interface.Deck], parent=None):
        super().__init__(parent)
        self.decks = decks
        logger.info(f'decks: {decks}')
        self.result_deck_subset: Optional[api.NewDeckSubset] = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Create Deck Subset")
        layout = QVBoxLayout()

        # Deck selection
        deck_layout = QHBoxLayout()
        deck_label = QLabel("Select deck:")
        self.deck_combo = QComboBox()
        for deck in self.decks:
            self.deck_combo.addItem(deck.name, deck)
        self.deck_combo.currentIndexChanged.connect(self.update_subset_name)
        deck_layout.addWidget(deck_label)
        deck_layout.addWidget(self.deck_combo)
        layout.addLayout(deck_layout)

        # Deck subset name
        name_layout = QHBoxLayout()
        name_label = QLabel("Deck Subset name:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Set initial deck subset name
        if self.decks:
            self.name_edit.setText(f"{self.decks[0].name} Due Cards")

        # Card selection method
        self.due_cards_radio = QRadioButton("Due cards")
        self.filter_radio = QRadioButton("Card filter")
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.due_cards_radio)
        self.button_group.addButton(self.filter_radio)
        self.due_cards_radio.setChecked(True)
        layout.addWidget(self.due_cards_radio)
        layout.addWidget(self.filter_radio)

        # Filter input
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Enter card filter")
        self.filter_edit.setEnabled(False)
        layout.addWidget(self.filter_edit)

        # Connect radio buttons to enable/disable filter input
        self.due_cards_radio.toggled.connect(self.update_subset_name)
        self.filter_radio.toggled.connect(self.update_subset_name)


        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.name_edit.textChanged.connect(self.update_ok_button_state)

        # Connect filter input to enable/disable OK button
        self.filter_edit.textChanged.connect(self.update_ok_button_state)        

        # Initial OK button state
        self.update_ok_button_state()

    def update_subset_name(self):
        selected_deck = self.deck_combo.currentData()
        if selected_deck:
            if self.due_cards_radio.isChecked():
                self.name_edit.setText(f"{selected_deck.name} Due Cards")
            elif self.filter_radio.isChecked():
                self.name_edit.setText(f"{selected_deck.name} Filtered")

    def update_ok_button_state(self):
        if self.filter_radio.isChecked() and not self.filter_edit.text():
            self.ok_button.setEnabled(False)
        elif not self.name_edit.text():
            self.ok_button.setEnabled(False)
        else:
            self.ok_button.setEnabled(True)
        self.filter_edit.setEnabled(self.filter_radio.isChecked())

    def accept(self):
        selected_deck = self.deck_combo.currentData()
        self.result_deck_subset = api.NewDeckSubset(
            deck_name=selected_deck.name,
            deck_subset_name=self.name_edit.text(),
            anki_deck_id=selected_deck.id,
            anki_due_cards=self.due_cards_radio.isChecked(),
            anki_card_filter=self.filter_edit.text() if self.filter_radio.isChecked() else None
        )
        super().accept()

def create_deck_subset(decks: List[anki_interface.Deck], parent=None) -> Optional[api.NewDeckSubset]:
    dialog = CreateDeckSubsetDialog(decks, parent)
    return_value = dialog.exec()
    if return_value: # accepted
        return dialog.result_deck_subset
    return None



