import sys
import os

if hasattr(sys, '_pytest_mode'):
    # called from within a test run
    pass
else:

    # need to declare upfront whether we're doing crash reporting
    # ============================================================
    from . import constants
    if constants.ENABLE_SENTRY_CRASH_REPORTING:
        import sentry_sdk
        # check version. some anki addons package an obsolete version of sentry_sdk
        sentry_sdk_int_version = int(sentry_sdk.VERSION.replace('.', ''))
        if sentry_sdk_int_version >= 155:
            sys._sentry_crash_reporting = True

    # setup logger
    # ============

    from . import logging_utils
    logging_utils.configure_logging(
        constants.ENV_VAR_LOGGING_MODE,
        constants.ENV_VAR_LOGGING_FILE,
        constants.ENV_VAR_LOGGING_LEVEL)

    logger = logging_utils.get_child_logger(__name__)

    # setup sentry crash reporting
    # ============================

    if hasattr(sys, '_sentry_crash_reporting'):
        sentry_sdk.init(
            dsn="https://b5dc1da8235cac3c2619ce29a9a82d15@o968582.ingest.us.sentry.io/4511298044690432",
            traces_sample_rate=1.0,
            # Add data like request headers and IP for users,
            # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
            send_default_pii=True,
        )
    else:
        logger.info('disabling crash reporting')

    # initialize audiocards
    # ===================

    from . import gui
    gui.setup_gui()
