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
