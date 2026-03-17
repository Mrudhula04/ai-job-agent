#!/bin/bash
# Schedule this script to run daily at 8 AM using cron
# Run: crontab -e
# Add: 0 8 * * * /path/to/schedule_daily.sh

cd "$(dirname "$0")"
source venv/bin/activate
python3 job-scraper-smart.py
