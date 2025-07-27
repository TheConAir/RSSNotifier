# RSSNotifier

Discord bot + FreshRSS watcher that scans feed items, pulls XML, searches for your keywords, and quietly reports matches.
Features

    /alerts slash commands:

        /alerts add <term> – add a keyword

        /alerts remove <term> – remove a keyword

        /alerts list – list current keywords (ephemeral)

        /alerts rescan – rescan items and show matches (ephemeral)

    FreshRSS (Fever API) integration

    XML parsing with lxml

    Runs the bot standalone or alongside your long‑running monitor

# Quick Start

## 1) Create & activate venv
python -m venv .venv
## Windows PowerShell:
.\.venv\Scripts\Activate.ps1

## 2) Install deps
python -m pip install --upgrade pip
pip install -r requirements.txt

Create a .env in the project root:

# FreshRSS
FRESHRSS_HOST=http://<host>:<port>
FRESHRSS_USERNAME=<username>
FRESHRSS_PASSWORD=<password>

# Discord
DISCORD_BOT_TOKEN=<token>
GUILD_ID=<your_guild_id>

# Optional
DISCORD_WEBHOOK_URL=
REFRESH_INTERVAL=7

Run

Bot only (dev/testing):

python discord_bot.py

Monitor loop (starts bot in background):

python main.py

Tips

    Replies are ephemeral by default to avoid spamming channels.