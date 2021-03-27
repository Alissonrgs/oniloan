# python
import pytz

# django
from django.conf import settings

local_tz = pytz.timezone(settings.TIME_ZONE)


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)
