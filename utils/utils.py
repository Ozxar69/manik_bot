import pytz
from datetime import datetime

moscow_tz = pytz.timezone('Europe/Moscow')

CURRENT_DATETIME = datetime.now(moscow_tz)
CURRENT_DATETIME = CURRENT_DATETIME.replace(tzinfo=None)
