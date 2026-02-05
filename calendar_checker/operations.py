"""
Calendar operations module for fetching and managing calendar events
"""

from datetime import datetime, timedelta
import pytz
from googleapiclient.errors import HttpError

from .config import DEFAULT_CALENDAR_ID, TIMEZONE


def get_today_events(service, calendar_id=DEFAULT_CALENDAR_ID, enrich=False):
    """
    Fetch today's events from the specified calendar.
    "Today" is determined in the configured TIMEZONE (from env).
    
    Args:
        service: The Google Calendar service instance
        calendar_id: The calendar ID to fetch events from (default: 'primary')
        enrich: If True, add calculated fields (duration_minutes) to each event
        
    Returns:
        List of today's events (optionally enriched with duration_minutes field)
        
    Raises:
        HttpError: If an error occurs while fetching events
    """
    try:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        start_utc = start_of_day.astimezone(pytz.UTC)
        end_utc = end_of_day.astimezone(pytz.UTC)
        time_min = start_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        time_max = end_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        print(f'Getting meetings for today: {now.strftime("%A, %B %d, %Y")} ({TIMEZONE})')
        
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        items = events_result.get('items', [])
        events = [e for e in items if e.get('status') != 'cancelled']
        
        if not events:
            print('\nNo meetings found for today.')
            return []
        
        if enrich:
            events = _enrich_events(events)
        
        print(f'\nToday\'s meetings ({len(events)} total):')
        print('-' * 50)
        _display_events(events)
        
        return events
        
    except HttpError as error:
        print(f'An error occurred: {error}')
        raise


def _calculate_duration(event):
    """
    Calculate event duration in minutes.
    
    Args:
        event: Event object from Google Calendar API
        
    Returns:
        Duration in minutes, or None for all-day events / invalid structure
    """
    start_obj = event.get('start') if isinstance(event.get('start'), dict) else None
    end_obj = event.get('end') if isinstance(event.get('end'), dict) else None
    if not start_obj or not end_obj:
        return None
    
    start = start_obj.get('dateTime')
    end = end_obj.get('dateTime')
    if not start or not end:
        return None
    
    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        duration = (end_dt - start_dt).total_seconds() / 60
        return int(duration)
    except (ValueError, TypeError):
        return None


def _enrich_events(events):
    """
    Enrich events with calculated fields.
    Adds 'duration_minutes' field to each event.
    Skips events with invalid structure (no start/end).
    """
    enriched = []
    for event in events:
        if not isinstance(event.get('start'), dict) or not isinstance(event.get('end'), dict):
            continue
        enriched_event = event.copy()
        enriched_event['duration_minutes'] = _calculate_duration(event)
        enriched.append(enriched_event)
    return enriched


def _display_events(events):
    """
    Display events in a formatted manner with duration.
    Skips events without valid start.
    """
    for event in events:
        start_obj = event.get('start')
        if not isinstance(start_obj, dict):
            continue
        start = start_obj.get('dateTime') or start_obj.get('date')
        summary = event.get('summary', 'Без названия')
        
        if start and 'dateTime' in start_obj:
            try:
                start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = start_time.strftime('%H:%M')
            except (ValueError, TypeError):
                time_str = '?'
            duration = event.get('duration_minutes')
            if duration is None:
                duration = _calculate_duration(event)
            if duration:
                print(f"  {time_str} - {summary} ({duration} мин)")
            else:
                print(f"  {time_str} - {summary}")
        else:
            print(f"  Весь день - {summary}")


def get_events_in_range(service, start_date, end_date, calendar_id=DEFAULT_CALENDAR_ID, enrich=False):
    """
    Fetch events within a specific date range.
    
    Args:
        service: The Google Calendar service instance
        start_date: Start datetime object
        end_date: End datetime object
        calendar_id: The calendar ID to fetch events from (default: 'primary')
        enrich: If True, add calculated fields (duration_minutes) to each event
        
    Returns:
        List of events in the specified range (optionally enriched)
        
    Raises:
        HttpError: If an error occurs while fetching events
    """
    try:
        time_min = start_date.isoformat() + 'Z'
        time_max = end_date.isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        items = events_result.get('items', [])
        events = [e for e in items if e.get('status') != 'cancelled']
        if enrich:
            events = _enrich_events(events)
        return events
        
    except HttpError as error:
        print(f'An error occurred: {error}')
        raise
