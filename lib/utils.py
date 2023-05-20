import datetime

import pytz


def est_time_now():
    """
    Returns the time in EST right now formatted as yyyy-mm-dd-hh-mm-ss
    :return: EST in yyyy-mm-dd-hh-mm-ss
    """
    timezone = pytz.timezone('US/Eastern')
    current_time = datetime.datetime.now(timezone)
    return current_time.strftime('%Y-%m-%d-%H-%M-%S')
