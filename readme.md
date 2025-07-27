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


#Tips

Replies are ephemeral by default to avoid spamming channels.
