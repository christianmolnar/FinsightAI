"""
Utility functions for checking market hours and trading status
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)

def is_market_open() -> bool:
    """
    Check if US stock market is currently open
    Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
    
    Returns:
        bool: True if market is open, False otherwise
    """
    try:
        # Get current time in Eastern Time
        et_timezone = ZoneInfo('America/New_York')
        now_et = datetime.now(et_timezone)
        
        # Check if it's a weekday (0 = Monday, 6 = Sunday)
        if now_et.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Market opens at 9:30 AM ET
        market_open = time(9, 30)
        # Market closes at 4:00 PM ET
        market_close = time(16, 0)
        
        current_time = now_et.time()
        
        # Check if current time is within market hours
        is_open = market_open <= current_time < market_close
        
        return is_open
        
    except Exception as e:
        logger.error(f"Error checking market hours: {e}")
        # Default to closed if we can't determine
        return False


def get_market_status() -> dict:
    """
    Get detailed market status including next open/close time
    
    Returns:
        dict: Market status information
    """
    try:
        et_timezone = ZoneInfo('America/New_York')
        now_et = datetime.now(et_timezone)
        
        is_open = is_market_open()
        
        # Calculate next market event
        if is_open:
            # Market is open, next event is close at 4 PM today
            next_event = "Close"
            next_time = datetime.combine(now_et.date(), time(16, 0)).replace(tzinfo=et_timezone)
        else:
            # Market is closed, calculate next open
            current_time = now_et.time()
            current_day = now_et.weekday()
            
            # If it's before 9:30 AM on a weekday, opens today
            if current_day < 5 and current_time < time(9, 30):
                next_event = "Open"
                next_time = datetime.combine(now_et.date(), time(9, 30)).replace(tzinfo=et_timezone)
            # If it's after close on Friday or weekend, opens Monday
            elif current_day == 4 and current_time >= time(16, 0):  # Friday after close
                days_until_monday = 3
                next_event = "Open"
                next_date = now_et.date()
                from datetime import timedelta
                next_date = next_date + timedelta(days=days_until_monday)
                next_time = datetime.combine(next_date, time(9, 30)).replace(tzinfo=et_timezone)
            elif current_day >= 5:  # Saturday or Sunday
                days_until_monday = 7 - current_day
                next_event = "Open"
                next_date = now_et.date()
                from datetime import timedelta
                next_date = next_date + timedelta(days=days_until_monday)
                next_time = datetime.combine(next_date, time(9, 30)).replace(tzinfo=et_timezone)
            else:  # Weekday after close, opens tomorrow
                next_event = "Open"
                from datetime import timedelta
                next_date = now_et.date() + timedelta(days=1)
                next_time = datetime.combine(next_date, time(9, 30)).replace(tzinfo=et_timezone)
        
        # Calculate time until next event
        time_until = next_time - now_et
        hours_until = int(time_until.total_seconds() // 3600)
        minutes_until = int((time_until.total_seconds() % 3600) // 60)
        
        return {
            "is_open": is_open,
            "status": "Open" if is_open else "Closed",
            "next_event": next_event,
            "next_time": next_time.strftime("%I:%M %p %Z"),
            "time_until": f"{hours_until}h {minutes_until}m" if hours_until > 0 else f"{minutes_until}m",
            "current_time": now_et.strftime("%I:%M %p %Z")
        }
        
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        return {
            "is_open": False,
            "status": "Unknown",
            "error": str(e)
        }
