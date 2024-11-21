import sys
import os

if hasattr(sys, '_pytest_mode'):
    # called from within a test run
    pass
else:
        
    # setup logger
    # ============

    from . import constants
    from . import logging_utils
    logging_utils.configure_logging(
        constants.ENV_VAR_LOGGING_MODE, 
        constants.ENV_VAR_LOGGING_FILE, 
        constants.ENV_VAR_LOGGING_LEVEL)

    # initialize audiocards
    # ===================

    from . import gui
    gui.setup_gui()    

