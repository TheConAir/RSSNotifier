import os
from dotenv import load_dotenv

load_dotenv()

# FreshRSS Settings
FRESHRSS_HOST = os.getenv('FRESHRSS_HOST')
FRESHRSS_USERNAME = os.getenv('FRESHRSS_USERNAME')
FRESHRSS_PASSWORD = os.getenv('FRESHRSS_PASSWORD')

# Discord Settings
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # For future use
GUILD_ID = int(os.getenv("GUILD_ID"))

# Scraper Settings
REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', 60))
DEFAULT_SEARCH_TERMS = ["Deep Sea Mining"]