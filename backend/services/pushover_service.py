"""
Pushover Push Notification Service

Delivers true push notifications (badges, sounds, banners) to iOS/Android.
$5 one-time app purchase. No subscription required.

Railway env vars required:
  PUSHOVER_TOKEN     - API token from pushover.net/apps
  PUSHOVER_USER_KEY  - Your user key from pushover.net dashboard
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

# Priority constants
PRIORITY_LOW    = -1
PRIORITY_NORMAL =  0
PRIORITY_HIGH   =  1
PRIORITY_URGENT =  2  # requires retry + expire params


class PushoverService:
    """Push notification service via Pushover"""

    def __init__(self):
        self.token    = os.getenv("PUSHOVER_TOKEN")
        self.user_key = os.getenv("PUSHOVER_USER_KEY")
        self.enabled  = bool(self.token and self.user_key)

        if self.enabled:
            logger.info("✅ Pushover alerts enabled")
        else:
            logger.warning("⚠️ Pushover not configured — set PUSHOVER_TOKEN and PUSHOVER_USER_KEY in Railway env vars")

    def send(
        self,
        title: str,
        message: str,
        priority: str = "default",
        tags: Optional[list] = None,   # unused (Pushover doesn't use tags), kept for interface compat
        click_url: Optional[str] = None,
    ) -> bool:
        """
        Send a push notification via Pushover.

        priority maps: 'min'→-1, 'low'→-1, 'default'→0, 'high'→1, 'urgent'→1
        (urgent uses priority=1; true Pushover priority=2 requires retry/expire)
        """
        if not self.enabled:
            logger.debug(f"Pushover not configured — skipping: {title}")
            return False

        priority_map = {
            "min":     PRIORITY_LOW,
            "low":     PRIORITY_LOW,
            "default": PRIORITY_NORMAL,
            "high":    PRIORITY_HIGH,
            "urgent":  PRIORITY_HIGH,
        }
        p = priority_map.get(priority, PRIORITY_NORMAL)

        payload = {
            "token":   self.token,
            "user":    self.user_key,
            "title":   title,
            "message": message,
            "priority": p,
        }

        if click_url:
            payload["url"] = click_url
            payload["url_title"] = "Open Dashboard"

        try:
            response = requests.post(PUSHOVER_API_URL, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == 1:
                logger.info(f"✅ Pushover sent: {title}")
                return True
            else:
                logger.error(f"❌ Pushover error: {data.get('errors')}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Pushover send failed: {e}")
            return False

    # ── Convenience methods — same interface as NtfyService ──────────────────

    def send_opportunity_alert(
        self,
        symbol: str,
        strategy: str,
        confidence: float,
        reasoning: str,
        count: int = 1,
    ) -> bool:
        if count == 1:
            title   = f"Scanner: {symbol} ({confidence:.0%})"
            message = f"Strategy: {strategy}\n\n{reasoning[:300]}"
        else:
            title   = f"Scanner: {count} opportunities found"
            message = f"Top pick: {symbol} ({confidence:.0%})\nStrategy: {strategy}\n\nCheck Transaction Queue."

        return self.send(title=title, message=message, priority="high")

    def send_execution_alert(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        auto_executed: bool = False,
    ) -> bool:
        prefix  = "AUTO-EXECUTED" if auto_executed else "Executed"
        title   = f"{prefix}: {action} {quantity} {symbol}"
        message = f"Price: ${price:.2f}\nTotal: ${quantity * price:,.2f}"
        return self.send(title=title, message=message, priority="high")

    def send_circuit_breaker_alert(self, reason: str, pause_until: str) -> bool:
        return self.send(
            title="CIRCUIT BREAKER Triggered",
            message=f"Reason: {reason}\nPaused until: {pause_until}\n\nCheck dashboard.",
            priority="urgent",
        )

    def send_position_alert(
        self,
        symbol: str,
        status: str,
        pnl_pct: float,
        message: str,
    ) -> bool:
        title = f"Position: {symbol} {status} ({pnl_pct:+.1f}%)"
        priority = "high" if status in ("SELL", "WARNING") else "default"
        return self.send(title=title, message=message, priority=priority)


# Singleton
_pushover_service: Optional[PushoverService] = None


def get_pushover_service() -> PushoverService:
    global _pushover_service
    if _pushover_service is None:
        _pushover_service = PushoverService()
    return _pushover_service
