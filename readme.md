# RSSNotifier

Discord bot + FreshRSS watcher that scans feed items, pulls XML, searches for your keywords, and reports matches.

# Features:


### Discord Integration:
Integrates with discord via webhooks to give automatic updates as well as via a discord bot to utilize slash commands.

<br />

Slash commands can be used to get current search terms, update search terms, and manually rescan all items in the RSS feed after updating search terms.
#### /alerts slash commands:

        /alerts add <term> – add a keyword

        /alerts remove <term> – remove a keyword

        /alerts list – list current keywords (ephemeral)

        /alerts rescan – rescan items and show matches (ephemeral)
### FreshRSS (Fever API) integration

### XML parsing with lxml

## Tips

- Replies are ephemeral by default to avoid spamming channels.

## Running tests

Install dependencies and run the test suite using [pytest](https://pytest.org/):

```bash
pip install -r requirements.txt
pytest
```

## Setup

Create a `.env` file with the required environment variables:

```
FRESHRSS_HOST=<your FreshRSS host>
FRESHRSS_USERNAME=<your username>
FRESHRSS_PASSWORD=<your password>
DISCORD_WEBHOOK_URL=<webhook url>
DISCORD_TOKEN=<bot token>
# optional, defaults to 0
GUILD_ID=<guild id>
```

Install the dependencies and start the bot:

```bash
pip install -r requirements.txt
python main.py
```

