

ENABLE_SENTRY_CRASH_REPORTING = True

ENV_VAR_LOGGING_MODE = 'AUDIOCARDS_LOGGING_MODE'
ENV_VAR_LOGGING_FILE = 'AUDIOCARDS_LOGGING_FILE'
ENV_VAR_LOGGING_LEVEL = 'AUDIOCARDS_LOGGING_LEVEL'

LOGGER_NAME = 'audiocards'
LOGGER_NAME_TEST = 'test_audiocards'

VOCABAI_API_HOSTNAME = 'app.vocabai.app'
VOCABAI_API_BASE_URL = 'https://app.vocabai.app/audiocards-api/v1'

# maximum number of days ahead when looking for due cards
MAX_DAYS_AHEAD = 10
# minimum number of cards we want in a due set
MIN_CARDS = 100