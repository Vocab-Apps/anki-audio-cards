# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anki add-on that syncs card data with the AudioCards API (vocabai.dev) for generating audio flashcard materials. The add-on uploads card information including templates, field data, and review history to enable audio generation from Anki decks.

## Development Environment Setup

### Virtual Environment
The project uses a Python virtual environment located at `${HOME}/python-env/anki-audio-cards/bin/activate`.

### Dependencies
Install dependencies with:
```bash
pip install -r requirements.txt
```

Key dependencies:
- PyQt6 (pinned to 6.4.2 to avoid crashes in unit tests)
- aqt[qt6] (Anki Qt interface)
- anki (Anki core library)
- pytest, pytest-qt, coverage (testing)

### Development Workflow
The `.tmuxp.yaml` file defines a tmux session with windows for:
- Main development work
- Git operations
- AudioCards log monitoring: `tail -f ${HOME}/logs/audiocards.log`
- Anki log monitoring: `tail -f ${HOME}/logs/anki.log`

Launch with: `tmuxp load .tmuxp.yaml`

### Environment Variables for Logging
The add-on supports configurable logging via environment variables:
- `AUDIOCARDS_LOGGING_MODE`: Logging mode
- `AUDIOCARDS_LOGGING_FILE`: Log file path
- `AUDIOCARDS_LOGGING_LEVEL`: Log level (DEBUG, INFO, etc.)

## Architecture

### Entry Point Flow
1. `__init__.py` (root): Sets up sys.path and imports `audiocards_addon`
2. `audiocards_addon/__init__.py`: Configures logging, then calls `gui.setup_gui()` to register menu items
3. User actions trigger functions in `logic.py` which orchestrate the sync workflow

### Core Components

**gui.py**: Menu registration
- Adds "AudioCards" menu to Anki browser and Tools menu
- Actions: "Sync All Decks", "Register New Deck", "card debug info"

**logic.py**: High-level orchestration
- `sync_all_decks_with_audiocards()`: Main sync entry point
- `register_new_deck()`: Creates new deck subsets via dialog
- Coordinates between `anki_interface.py` and `api.py`

**anki_interface.py**: Anki data layer
- Queries Anki's collection database for decks, cards, notes
- Key types: `Deck`, `CardFormat` (note_type_id + card_ord)
- `iterate_due_cards_slices()`: Adaptive card fetching (looks ahead up to `MAX_DAYS_AHEAD` days to find at least `MIN_CARDS` cards)
- `build_card_data()`: Constructs card payload with fields, reviews, due times
- Card due time calculation varies by card type (learning/relearning vs review)

**api.py**: AudioCards API client
- Base URL: `https://app.vocabai.dev/audiocards-api/v1`
- Key methods:
  - `list_deck_subsets()`: Get configured deck subsets
  - `list_deck_card_formats()`: Get existing card formats for a deck
  - `create_deck_card_format()`: Register new card template with field samples
  - `create_update_cards()`: Upload cards in batches (max 100 per request)
- Uses API key from Anki add-on config

**dialogs.py**: Qt dialogs
- `CreateDeckSubsetDialog`: Dialog for registering new decks with options for "Due cards" or custom "Card filter"

**constants.py**: Configuration constants
- `MAX_DAYS_AHEAD = 10`: Maximum days to look ahead for due cards
- `MIN_CARDS = 100`: Minimum cards needed for audio generation
- Logger names and environment variable names

**logging_utils.py**: Logging configuration
- Centralized logger setup using `constants.LOGGER_NAME`

### Sync Workflow
1. Fetch registered deck subsets from API (`list_deck_subsets()`)
2. For each deck subset:
   - Build browser query for due/new cards
   - Query existing card formats from API
   - Detect unknown card formats, create them on API (includes templates and field samples)
   - Iterate cards in slices of 100
   - Build card data with fields, review history, due times
   - Upload to API via `create_update_cards()`

### Card Format Registration
When an unknown card format is encountered:
1. Extract front/back templates from Anki note type
2. Sample up to 100 card fields from the deck
3. Send to API to create the format entry
4. Refresh card format map and continue syncing

## Configuration

### API Key
Stored in Anki add-on config (`config.json`) with key `api_key`. Also stored in `meta.json` (appears to be Anki add-on metadata).

### Deck Subsets
Created via "AudioCards: Register New Deck" in Tools menu. Each subset specifies:
- Anki deck ID and name
- Whether to sync due cards
- Optional custom card filter

## Testing

While test files weren't found in the repository, the code includes test infrastructure:
- `sys._pytest_mode` check in `__init__.py` to skip GUI initialization during tests
- `constants.LOGGER_NAME_TEST` for test logging
- pytest and pytest-qt in requirements

## Code Patterns

### Logging
All modules use child loggers:
```python
from . import logging_utils
logger = logging_utils.get_child_logger(__name__)
```

### Anki Collection Access
Access via global `aqt.mw.col` (main window collection):
```python
card_ids = aqt.mw.col.find_cards(browser_query)
card = aqt.mw.col.get_card(card_id)
```

### Dataclasses
Used extensively for API data structures (DeckSubset, DeckCardFormat, NewDeckSubset, NewCardFormat) and internal types (Deck, CardFormat).

### Card Type Handling
Due time calculation differs by card type:
- `CARD_TYPE_NEW`: Uses `card.due` as new_rank
- `CARD_TYPE_LRN`, `CARD_TYPE_RELEARNING`: `card.due` is Unix timestamp
- `CARD_TYPE_REV`: `card.due` is days since collection creation (requires scheduler timing calculation)
