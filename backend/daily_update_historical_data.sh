#!/bin/bash

# Daily Historical Data Update Script
# Run this via cron: 0 19 * * 1-5 (7 PM ET Monday-Friday after market close)

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run daily update
python setup_historical_data.py --daily-update

# Log completion
echo "[$(date)] Historical data daily update completed" >> /tmp/historical_data_update.log
