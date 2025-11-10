#!/usr/bin/env python3
"""
HTTPS server for development with Schwab API integration
"""

import uvicorn
import ssl
import os

if __name__ == "__main__":
    # SSL context for HTTPS
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile="ssl/cert.pem", 
        keyfile="ssl/key.pem"
    )
    
    print("� Starting HTTPS server on https://localhost:8000")
    print("📋 Use this callback URL in Schwab Developer Portal:")
    print("    https://localhost:8000/api/auth/schwab/callback")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="ssl/key.pem",
        ssl_certfile="ssl/cert.pem",
        reload=True,
        log_level="info"
    )
