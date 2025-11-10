"""
Charles Schwab API Authentication Endpoints
Handles OAuth 2.0 flow for Schwab API integration
"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import logging
from typing import Optional
import os

from ..schwab_api import SchwabAPIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Get the Schwab API service instance
schwab_service = SchwabAPIService()

@router.get("/schwab/login")
async def schwab_login():
    """
    Start the Schwab OAuth flow
    Redirects user to Schwab authorization page
    """
    try:
        if not schwab_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Schwab API not configured. Please set APP_KEY and APP_SECRET in environment variables."
            )
        
        # Generate authorization URL
        auth_url = schwab_service.get_authorization_url()
        
        if not auth_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate authorization URL"
            )
        
        logger.info("Redirecting to Schwab authorization URL")
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating Schwab login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schwab/callback")
async def schwab_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """
    Handle the OAuth callback from Schwab
    Exchange authorization code for access token
    """
    try:
        # Check for OAuth errors
        if error:
            logger.error(f"OAuth error: {error} - {error_description}")
            return HTMLResponse(
                content=f"""
                <html>
                    <head><title>Schwab API Authorization Failed</title></head>
                    <body>
                        <h2>Authorization Failed</h2>
                        <p>Error: {error}</p>
                        <p>Description: {error_description or 'No description provided'}</p>
                        <p><a href="/api/auth/schwab/login">Try Again</a></p>
                    </body>
                </html>
                """,
                status_code=400
            )
        
        # Check for authorization code
        if not code:
            return HTMLResponse(
                content="""
                <html>
                    <head><title>Schwab API Authorization Failed</title></head>
                    <body>
                        <h2>Authorization Failed</h2>
                        <p>No authorization code received from Schwab.</p>
                        <p><a href="/api/auth/schwab/login">Try Again</a></p>
                    </body>
                </html>
                """,
                status_code=400
            )
        
        # Exchange code for tokens
        logger.info("Received authorization code, exchanging for tokens")
        tokens = await schwab_service.exchange_code_for_tokens(code)
        
        if tokens:
            logger.info("Successfully obtained Schwab API tokens")
            return HTMLResponse(
                content="""
                <html>
                    <head><title>Schwab API Authorization Successful</title></head>
                    <body>
                        <h2>✅ Authorization Successful!</h2>
                        <p>Your Schwab API connection has been established.</p>
                        <p>You can now close this window and return to the application.</p>
                        <script>
                            // Auto-close window after 3 seconds
                            setTimeout(() => {
                                if (window.opener) {
                                    window.opener.postMessage('schwab-auth-success', '*');
                                    window.close();
                                } else {
                                    window.location.href = '/';
                                }
                            }, 3000);
                        </script>
                    </body>
                </html>
                """
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to exchange authorization code for tokens"
            )
            
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Schwab API Authorization Error</title></head>
                <body>
                    <h2>Authorization Error</h2>
                    <p>An error occurred during authorization: {str(e)}</p>
                    <p><a href="/api/auth/schwab/login">Try Again</a></p>
                </body>
            </html>
            """,
            status_code=500
        )


@router.get("/schwab/status")
async def schwab_status():
    """
    Check the current Schwab API authentication status
    """
    try:
        if not schwab_service.is_configured():
            return {
                "authenticated": False,
                "configured": False,
                "message": "Schwab API credentials not configured"
            }
        
        is_authenticated = await schwab_service.is_authenticated()
        
        return {
            "authenticated": is_authenticated,
            "configured": True,
            "message": "Ready for authentication" if not is_authenticated else "Authenticated and ready"
        }
        
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return {
            "authenticated": False,
            "configured": False,
            "error": str(e)
        }


@router.post("/schwab/logout")
async def schwab_logout():
    """
    Logout from Schwab API (clear tokens)
    """
    try:
        await schwab_service.logout()
        return {"message": "Successfully logged out from Schwab API"}
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schwab/refresh")
async def schwab_refresh_token():
    """
    Manually refresh the Schwab API token
    """
    try:
        success = await schwab_service.refresh_token()
        
        if success:
            return {"message": "Token refreshed successfully"}
        else:
            raise HTTPException(
                status_code=401,
                detail="Failed to refresh token. Please re-authenticate."
            )
            
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail=str(e))
