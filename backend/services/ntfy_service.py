"""
ntfy.sh Push Notification Service

Sends push notifications via ntfy.sh to the ntfy app on your phone.
Free tier: 250 messages/day — more than sufficient for trade alerts.

Setup:
1. Install ntfy app on your phone (iOS/Android)
2. Subscribe to your topic (e.g. "finsight-alerts")
3. Set NTFY_TOKEN and NTFY_TOPIC in Railway env vars

Railway env vars required:
  NTFY_TOKEN   - Access token from ntfy.sh account settings
  NTFY_TOPIC   - Your topic name (e.g. "finsight-alerts")
  NTFY_URL     - Optional, defaults to https://ntfy.sh
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

NTFY_DEFAULT_URL = "https://ntfy.sh"


class NtfyService:
    """Push notification service via ntfy.sh"""

    def __init__(self):
        self.token = os.getenv("NTFY_TOKEN")
        self.topic = os.getenv("NTFY_TOPIC", "finsight-alerts")
        self.base_url = os.getenv("NTFY_URL", NTFY_DEFAULT_URL).rstrip("/")
        self.enabled = bool(self.token and self.topic)

        if self.enabled:
            logger.info(f"✅ ntfy.sh alerts enabled → topic: {self.topic}")
        else:
            logger.warning("⚠️ ntfy.sh not configured (set NTFY_TOKEN and NTFY_TOPIC)")

    def send(
        self,
        title: str,
        message: str,
        priority: str = "default",
        tags: Optional[list] = None,
        click_url: Optional[str] = None,
    ) -> bool:
        """
        Send a push notification.

        Priority options: min, low, default, high, urgent
        Tags: emoji shortcodes shown as icons (e.g. ["chart_increasing", "bell"])

        Returns True if sent successfully.
        """
        if not self.enabled:
            logger.debug(f"ntfy not configured — skipping: {title}")
            return False

        url = f"{self.base_url}/{self.topic}"
        # HTTP headers must be latin-1 safe — encode non-ASCII chars as UTF-8 then
        # use the RFC 5987 workaround: just strip/replace emojis in the Title header
        # and keep them in the message body instead.
        safe_title = title.encode("ascii", errors="ignore").decode("ascii").strip() or "f.Insight.AI Alert"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Title": safe_title,
            "Priority": priority,
            "Content-Type": "text/plain; charset=utf-8",
        }

        if tags:
            headers["Tags"] = ",".join(tags)

        if click_url:
            headers["Click"] = click_url

        try:
            response = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ ntfy sent: {title}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ntfy send failed: {e}")
            return False

    # ── Convenience methods matching alert_service interface ──────────────────

    def send_opportunity_alert(
        self,
        symbol: str,
        strategy: str,
        confidence: float,
        reasoning: str,
        count: int = 1,
    ) -> bool:
        if count == 1:
            title = f"🎯 Scanner: {symbol} ({confidence:.0%})"
            message = f"Strategy: {strategy}\n\n{reasoning[:200]}"
        else:
            title = f"🎯 Scanner: {count} opportunities found"
            message = f"Top pick: {symbol} ({confidence:.0%})\nStrategy: {strategy}\n\nCheck Transaction Queue."

        return self.send(
            title=title,
            message=message,
            priority="high",
            tags=["chart_increasing", "bell"],
        )

    def send_execution_alert(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        auto_executed: bool = False,
    ) -> bool:
        prefix = "🤖 Auto-Executed" if auto_executed else "✅ Executed"
        title = f"{prefix}: {action} {quantity} {symbol}"
        message = f"Price: ${price:.2f}\nTotal: ${quantity * price:,.2f}"

        return self.send(
            title=title,
            message=message,
            priority="high",
            tags=["white_check_mark" if not auto_executed else "robot"],
        )

    def send_circuit_breaker_alert(self, reason: str, pause_until: str) -> bool:
        return self.send(
            title="🚨 Circuit Breaker Triggered",
            message=f"Reason: {reason}\nPaused until: {pause_until}\n\nCheck dashboard.",
            priority="urgent",
            tags=["rotating_light"],
        )

    def send_position_alert(
        self,
        symbol: str,
        status: str,
        pnl_pct: float,
        message: str,
    ) -> bool:
        emoji = {"SELL": "🔴", "BUY_MORE": "💰", "WARNING": "⚠️", "TARGET": "🎯"}.get(status, "📊")
        return self.send(
            title=f"{emoji} Position: {symbol} {status} ({pnl_pct:+.1f}%)",
            message=message,
            priority="high" if status in ("SELL", "WARNING") else "default",
            tags=["chart_with_upwards_trend"],
        )


# Singleton
_ntfy_service: Optional[NtfyService] = None


def get_ntfy_service() -> NtfyService:
    global _ntfy_service
    if _ntfy_service is None:
        _ntfy_service = NtfyService()
    return _ntfy_service
