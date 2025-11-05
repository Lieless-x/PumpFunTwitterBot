#!/bin/bash

# Start script for Pump.fun Dump Tracker Bot

# Set Twitter API credentials
export TWITTER_API_KEY="your key here"
export TWITTER_API_SECRET="your key here"
export TWITTER_BEARER_TOKEN="your key here"
export TWITTER_ACCESS_TOKEN="your key here"
export TWITTER_ACCESS_SECRET="your key here"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the bot with any arguments passed to this script
python3 pumpfun_tracker.py "$@"
