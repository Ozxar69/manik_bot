from datetime import datetime

import pytz


def get_current_time():
    moscow_tz = pytz.timezone("Europe/Moscow")

    CURRENT_DATETIME = datetime.now(moscow_tz)
    CURRENT_DATETIME = CURRENT_DATETIME.replace(tzinfo=None)
    return CURRENT_DATETIME
