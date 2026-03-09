"""
Alert Service - Send notifications for important events

Delegates to ntfy.sh push notification service.
Install the ntfy app on your phone and subscribe to your topic.

Railway env vars required:
  NTFY_TOKEN   - Access token from ntfy.sh account settings
  NTFY_TOPIC   - Your topic name (e.g. "finsight-alerts")
"""

import logging
from typing import Optional
from services.ntfy_service import get_ntfy_service

logger = logging.getLogger(__name__)


class AlertService:
    """Send alerts for scanner opportunities and trading events"""

    def __init__(self):
        self._ntfy = get_ntfy_service()
        if self._ntfy.enabled:
            logger.info("✅ Push alerts enabled via ntfy.sh")
        else:
            logger.warning("⚠️ Alerts disabled — set NTFY_TOKEN and NTFY_TOPIC in Railway env vars")

    def send_opportunity_alert(
        self,
        symbol: str,
        strategy: str,
        confidence: float,
        reasoning: str,
        count: int = 1,
    ) -> bool:
        return self._ntfy.send_opportunity_alert(symbol, strategy, confidence, reasoning, count)

    def send_execution_alert(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        auto_executed: bool = False,
    ) -> bool:
        return self._ntfy.send_execution_alert(symbol, action, quantity, price, auto_executed)

    def send_circuit_breaker_alert(self, reason: str, pause_until: str) -> bool:
        return self._ntfy.send_circuit_breaker_alert(reason, pause_until)

    def send_position_alert(
        self, symbol: str, status: str, pnl_pct: float, message: str
    ) -> bool:
        return self._ntfy.send_position_alert(symbol, status, pnl_pct, message)


# Singleton instance
_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    """Get singleton alert service instance"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
