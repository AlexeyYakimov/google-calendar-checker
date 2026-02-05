"""
Google Calendar Checker - A Python package to interact with Google Calendar
"""

from .auth import get_calendar_service
from .operations import get_today_events, get_events_in_range
from .scheduler import CalendarPoller
from .cache import save_events_to_cache, load_events_from_cache, get_cache_info, is_cache_fresh

__all__ = [
    'get_calendar_service',
    'get_today_events',
    'get_events_in_range',
    'CalendarPoller',
    'save_events_to_cache',
    'load_events_from_cache',
    'get_cache_info',
    'is_cache_fresh'
]
__version__ = '1.0.0'
