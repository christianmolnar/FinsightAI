"""
Alert Service - Send notifications for important events

Supports:
- SMS via Twilio (free tier)
- Future: Email, Discord, Telegram
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AlertService:
    """Send alerts for scanner opportunities and trading events"""
    
    def __init__(self):
        """Initialize alert service with Twilio credentials from env"""
        self.twilio_enabled = False
        self.phone_to = os.getenv("ALERT_PHONE_TO")
        
        # Check if Twilio is configured
        if all([
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
            os.getenv("TWILIO_PHONE_FROM"),
            self.phone_to
        ]):
            try:
                from twilio.rest import Client
                self.twilio_client = Client(
                    os.getenv("TWILIO_ACCOUNT_SID"),
                    os.getenv("TWILIO_AUTH_TOKEN")
                )
                self.phone_from = os.getenv("TWILIO_PHONE_FROM")
                self.twilio_enabled = True
                logger.info("✅ Twilio SMS alerts enabled")
            except ImportError:
                logger.warning("⚠️ Twilio library not installed. Run: pip install twilio")
            except Exception as e:
                logger.error(f"❌ Twilio initialization failed: {e}")
        else:
            logger.info("ℹ️ Twilio not configured (SMS alerts disabled)")
    
    def send_opportunity_alert(
        self,
        symbol: str,
        strategy: str,
        confidence: float,
        reasoning: str,
        count: int = 1
    ) -> bool:
        """
        Send alert when scanner finds opportunities
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            strategy: Strategy name (e.g., "technical_breakout")
            confidence: AI confidence (0.0-1.0)
            reasoning: Brief reasoning from AI
            count: Total opportunities found in scan
            
        Returns:
            True if alert sent successfully, False otherwise
        """
        # Format message
        if count == 1:
            message = (
                f"🎯 f.insight Scanner Alert\n\n"
                f"Symbol: {symbol}\n"
                f"Strategy: {strategy}\n"
                f"Confidence: {confidence:.0%}\n\n"
                f"{reasoning[:100]}..."
            )
        else:
            message = (
                f"🎯 f.insight Scanner Alert\n\n"
                f"Found {count} opportunities!\n\n"
                f"Top: {symbol} ({confidence:.0%})\n"
                f"Strategy: {strategy}\n\n"
                f"Check Transaction Queue for details."
            )
        
        return self._send_sms(message)
    
    def send_execution_alert(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        auto_executed: bool = False
    ) -> bool:
        """
        Send alert when trade is executed
        
        Args:
            symbol: Stock symbol
            action: "BUY" or "SELL"
            quantity: Number of shares
            price: Execution price
            auto_executed: True if automatically executed
            
        Returns:
            True if alert sent successfully
        """
        auto_text = "🤖 AUTO-EXECUTED" if auto_executed else "✅ EXECUTED"
        
        message = (
            f"{auto_text}\n\n"
            f"{action} {quantity} {symbol}\n"
            f"Price: ${price:.2f}\n"
            f"Total: ${quantity * price:,.2f}"
        )
        
        return self._send_sms(message)
    
    def send_circuit_breaker_alert(
        self,
        reason: str,
        pause_until: str
    ) -> bool:
        """
        Send alert when circuit breaker triggers
        
        Args:
            reason: Why circuit breaker triggered
            pause_until: When trading will resume
            
        Returns:
            True if alert sent successfully
        """
        message = (
            f"🚨 CIRCUIT BREAKER TRIGGERED\n\n"
            f"Reason: {reason}\n"
            f"Paused until: {pause_until}\n\n"
            f"Check dashboard for details."
        )
        
        return self._send_sms(message)
    
    def _send_sms(self, message: str) -> bool:
        """
        Internal method to send SMS via Twilio
        
        Args:
            message: Text message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.twilio_enabled:
            logger.debug(f"SMS not sent (Twilio disabled): {message}")
            return False
        
        try:
            msg = self.twilio_client.messages.create(
                body=message,
                from_=self.phone_from,
                to=self.phone_to
            )
            logger.info(f"✅ SMS sent: {msg.sid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ SMS send failed: {e}")
            return False


# Singleton instance
_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    """Get singleton alert service instance"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
