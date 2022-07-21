import pytz
from disposable_email_domains import blocklist


def is_email_temporary(email):
    return email.strip().split("@")[1] in blocklist


def is_timezone_correct(tz):
    tz in pytz.all_timezones_set
