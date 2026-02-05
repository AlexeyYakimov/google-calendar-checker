"""
Scheduler module for periodic calendar polling
"""

import logging
from datetime import datetime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .auth import get_calendar_service
from .operations import get_today_events
from .cache import save_events_to_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalendarPoller:
    """
    Calendar polling service that runs on a schedule.
    """
    
    def __init__(self, timezone='Europe/Moscow', start_hour=9, end_hour=19, interval_minutes=30):
        """
        Initialize the calendar poller.
        
        Args:
            timezone: Timezone for scheduling (default: Europe/Moscow)
            start_hour: Start hour for polling (default: 9)
            end_hour: End hour for polling (default: 19)
            interval_minutes: Polling interval in minutes (default: 30)
        """
        self.timezone = pytz.timezone(timezone)
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.interval_minutes = interval_minutes
        self.scheduler = BlockingScheduler(timezone=self.timezone)
        self.service = None
        
    def _initialize_service(self):
        """Initialize the Google Calendar service."""
        if self.service is None:
            logger.info("Initializing Google Calendar service...")
            self.service = get_calendar_service()
            logger.info("Google Calendar service initialized successfully")
    
    def poll_calendar(self, silent=False):
        """
        Poll the calendar for today's events.
        This is the job that runs on schedule.
        
        Args:
            silent: If True, only initialize service without displaying events
        """
        try:
            current_time = datetime.now(self.timezone)
            
            # Check if we're within operating hours
            if not (self.start_hour <= current_time.hour < self.end_hour):
                if not silent:
                    logger.info(f"Outside operating hours. Current time: {current_time.strftime('%H:%M')}")
                return
            
            if not silent:
                logger.info("=" * 60)
                logger.info(f"Polling calendar at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                logger.info("=" * 60)
            
            # Initialize service if needed
            self._initialize_service()
            
            if silent:
                # Silent mode: just fetch data without displaying
                logger.info("Service initialized and ready")
                return
            
            # Fetch today's events with enrichment (duration_minutes)
            events = get_today_events(self.service, enrich=True)
            
            # Save to cache for notifier
            save_events_to_cache(
                events,
                metadata={
                    'source': 'calendar_poller',
                    'timezone': str(self.timezone),
                    'polled_at': current_time.isoformat()
                }
            )
            
            if events:
                logger.info(f"Found {len(events)} event(s) for today")
            else:
                logger.info("No events found for today")
                
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error polling calendar: {e}", exc_info=True)
    
    def start(self):
        """
        Start the polling scheduler.
        Runs at specific times (on the hour and half-hour) between start_hour and end_hour.
        """
        logger.info("=" * 60)
        logger.info("Starting Calendar Poller Service")
        logger.info(f"Timezone: {self.timezone}")
        logger.info(f"Operating hours: {self.start_hour}:00 - {self.end_hour}:00")
        logger.info(f"Polling schedule: :00 and :30 of each hour")
        logger.info("=" * 60)
        
        # Run initial poll to show current events
        logger.info("Running initial poll...")
        logger.info("")
        self.poll_calendar()
        
        current_time = datetime.now(self.timezone)
        logger.info("")
        logger.info(f"Current time: {current_time.strftime('%H:%M:%S')}")
        logger.info("Next polls will occur at :00 and :30 of each hour")
        logger.info("=" * 60)
        
        # Schedule the job to run at :00 and :30 of each hour
        # The job itself checks if we're within operating hours
        self.scheduler.add_job(
            self.poll_calendar,
            CronTrigger(minute='0,30', timezone=self.timezone),
            id='calendar_poll',
            name='Poll Google Calendar',
            replace_existing=True
        )
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler...")
            self.scheduler.shutdown()
            logger.info("Scheduler stopped.")
