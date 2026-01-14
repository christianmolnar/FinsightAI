"""
Models Package

Import all models for easy access and to ensure they're registered with SQLAlchemy.
"""

from app.models.user import User
from app.models.portfolio import Portfolio, Trade
from app.models.pending_transaction import PendingTransaction
from models.watchlist import UserWatchlist
from models.preferences import UserPreferences

__all__ = [
    "User",
    "Portfolio",
    "Trade",
    "PendingTransaction",
    "UserWatchlist",
    "UserPreferences",
]
