"""
Models Package

Import all models for easy access and to ensure they're registered with SQLAlchemy.
"""

from models.watchlist import UserWatchlist
from models.preferences import UserPreferences

__all__ = [
    "UserWatchlist",
    "UserPreferences",
]
