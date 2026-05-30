import os

ENABLE_SENTRY_CRASH_REPORTING = True

ENV_VAR_LOGGING_MODE = 'AUDIOCARDS_LOGGING_MODE'
ENV_VAR_LOGGING_FILE = 'AUDIOCARDS_LOGGING_FILE'
ENV_VAR_LOGGING_LEVEL = 'AUDIOCARDS_LOGGING_LEVEL'

LOGGER_NAME = 'audiocards'
LOGGER_NAME_TEST = 'test_audiocards'

# Anki names the installed addon directory by its manifest "package" value
# ('audiocards'), or by the numeric AnkiWeb id, or 'anki-audio-cards' in a dev
# symlink setup -- never reliably by the git folder name. Derive the real
# package name from this file's on-disk location so addonManager can locate
# meta.json. Hardcoding it broke writeConfig/getConfig for real installs
# (Sentry ANKI-AUDIO-CARDS-2 / ANKI-AUDIO-CARDS-3).
ADDON_PACKAGE_NAME = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

VOCABAI_API_HOSTNAME = 'app.vocab.ai'

# timeout (in seconds) for all HTTP requests to the AudioCards API
REQUEST_TIMEOUT_SECONDS = 60

# maximum number of days ahead when looking for due cards
MAX_DAYS_AHEAD = 10
# minimum number of cards we want in a due set
MIN_CARDS = 100

API_KEY_MISSING_MESSAGE = (
    'AudioCards API key is not configured. '
    'Please set it via Tools > AudioCards: Settings.'
)