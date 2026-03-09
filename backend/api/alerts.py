"""
Alerts API

Endpoints:
  POST /api/alerts/test  — send a test push notification via ntfy.sh
"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


DEFAULT_TEST_MESSAGE = "🧪 Test alert from f.Insight.AI — notifications are working!"


@router.post("/test")
async def send_test_alert(
    current_user=Depends(get_current_user),
):
    """Send a test push notification via ntfy.sh to confirm alerts are working."""
    try:
        from services.ntfy_service import get_ntfy_service
        ntfy = get_ntfy_service()

        if not ntfy.enabled:
            raise HTTPException(
                status_code=503,
                detail="ntfy.sh not configured — set NTFY_TOKEN and NTFY_TOPIC in Railway env vars",
            )

        sent = ntfy.send(
            title="🧪 f.Insight.AI Test Alert",
            message=DEFAULT_TEST_MESSAGE,
            priority="default",
            tags=["white_check_mark"],
        )

        if not sent:
            raise HTTPException(status_code=502, detail="ntfy.sh returned an error — check Railway logs")

        logger.info(f"Test alert sent by {current_user.email}")
        return {"sent": True, "topic": ntfy.topic, "message": DEFAULT_TEST_MESSAGE}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test alert failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
