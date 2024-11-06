from datetime import datetime, timedelta
import math
from typing import List


def to_seconds(time: timedelta) -> float:
    return time.total_seconds()


def RR(delta_time: float, K_value: float) -> float:
    """Return the retention rate of the user from 0 to 1

    Args:
        delta_time: the time since the last refresh in seconds
        K_value: the K value of the user
    """
    return math.exp(-delta_time / K_value)


def Ktime(Ltime: float, RR_to_refresh: float = 0.8) -> float:
    """Return the K value of the user

    Args:
        Ltime: delta time when the RR will reach RR_to_refresh
        RR_to_refresh: the retention rate to refresh the user
    """
    return -Ltime / math.log(RR_to_refresh)


def Lt(
    refresh_number: int, difficulty: float = 1, Ltmax: float = 31536000
) -> float:
    """Get the Loosing time dependig on the refresh number

    The loosing time is the time it takes for the user to reach RR_to_refresh

    Args:
        refresh_number: the number of refreshes
        S_value: the S value calculated depending on the complexity of the
            element
        Ltmax: the maximum loosing time in seconds, default is 1 year
    """
    difficulty = difficulty if difficulty >= 0 else 0
    return Ltmax / (
        1 + 132232.47 * math.exp(-2.3527 * (refresh_number - difficulty / 3))
    )


def retention_index(
    last_refresh: datetime | timedelta,
    refresh_number: int,
    difficulty: float,
    RR_to_refresh: float = 0.8,
) -> float:
    """Return the retention rate of the user from 0 to 1"""
    if isinstance(last_refresh, timedelta):
        delta_time = to_seconds(last_refresh)
    elif isinstance(last_refresh, datetime):
        delta_time = to_seconds(datetime.now() - last_refresh)
    else:
        raise TypeError("last_refresh must be a timedelta or a datetime object")
    K_value = Ktime(Lt(refresh_number, difficulty), RR_to_refresh)
    print(f"Lt: {Lt(refresh_number, difficulty)}")
    print(delta_time, K_value)
    return RR(delta_time, K_value)
