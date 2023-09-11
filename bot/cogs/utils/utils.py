from datetime import datetime as dt


def get_time_string() -> str:
    """
    The get_time_string function is used to get the current time
    :return: The current time in the form of a string
    """
    return dt.utcnow().__str__()


def progress_bar(percent):
    """
    The progress_bar function prints a progress bar to the console.

    :param percent: Display the percentage of completion
    :return: A string that represents a progress bar
    """
    bar_filled = "▓"
    bar_empty = "░"
    length = 15

    progress_bar = bar_filled * int((percent / (100.0 / length)))
    progress_bar += bar_empty * (length - len(progress_bar))
    return f"{progress_bar} {percent:.1f}%"
