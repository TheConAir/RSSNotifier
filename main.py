# main.py
import time
from threading import Thread
from loguru import logger

from scraper.search_engine import FederalRegisterSearcher
from config.settings import REFRESH_INTERVAL, GUILD_ID
from discord_bot import run_bot

def main():
    searcher = FederalRegisterSearcher()

    # Start Discord bot in the background
    t = Thread(target=run_bot, args=(searcher, GUILD_ID), daemon=True)
    t.start()

    logger.info("Starting Federal Register monitoring...")
    logger.info(f"Search terms: {searcher.get_search_terms()}")
    logger.info(f"Refresh interval: {REFRESH_INTERVAL} seconds")

    while True:
        try:
            found = searcher.process_unread_items()
            if found:
                logger.info(f"Processing complete. Found {len(found)} matching articles.")
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()
