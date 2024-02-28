import logging
import traceback
import rollbar
import sys
from app.utils.constants import DEBUG, ROLLBAR

logger = logging.getLogger(__name__)

def init_rollbar():
    #if not DEBUG:
    rollbar.init(**ROLLBAR)

def try_reporting_error_to_rollbar(extra_data=dict):
    try:
        # if not DEBUG:
        rollbar.report_exc_info(
            sys.exc_info(),
            extra_data=extra_data)
    except Exception:
        logger.error('Failed to post exception to Rollbar: {} {}'.format(
            str(extra_data), traceback.format_exc()))
