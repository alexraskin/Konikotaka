import time
from datetime import datetime as dt
from datetime import timezone


def get_time_string() -> str:
    return dt.now(tz=timezone.utc).__str__()


def progress_bar(percent) -> str:
    bar_filled = "▓"
    bar_empty = "░"
    length = 15

    progress_bar = bar_filled * int((percent / (100.0 / length)))
    progress_bar += bar_empty * (length - len(progress_bar))
    return f"{progress_bar} {percent:.1f}%"


def get_year_round() -> float:
    now = dt.now()
    year_end = dt(now.year + 1, 1, 1)
    year_start = dt(now.year, 1, 1)
    year_percent = (now - year_start) / (year_end - year_start) * 100
    return year_percent


def date(target, clock: bool = True, ago: bool = False, only_ago: bool = False) -> str:
    """Converts a timestamp to a Discord timestamp format"""
    if isinstance(target, int) or isinstance(target, float):
        target = dt.fromtimestamp(target)

    unix = int(time.mktime(target.timetuple()))
    timestamp = f"<t:{unix}:{'f' if clock else 'D'}>"
    if ago:
        timestamp += f" (<t:{unix}:R>)"
    if only_ago:
        timestamp = f"<t:{unix}:R>"
    return timestamp
