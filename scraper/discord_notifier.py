from discord_webhook import DiscordWebhook
from config.settings import DISCORD_WEBHOOK_URL
from loguru import logger


class DiscordNotifier:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or DISCORD_WEBHOOK_URL

    def send_notification(self, found_terms, xml_url, item_id=None):
        """Send a Discord notification about found articles"""
        try:
            terms_text = ", ".join(found_terms)
            message = f"{terms_text} was found in this document!"
            if item_id:
                message += f" (Article ID: {item_id})"
            message += f"\n{xml_url}"

            webhook = DiscordWebhook(url=self.webhook_url, content=message)
            response = webhook.execute()

            if response.status_code == 200:
                logger.info(f"Discord notification sent for terms: {terms_text}")
            else:
                logger.error(f"Failed to send Discord notification: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")


# ================================================================
# scraper/search_engine.py
from scraper.freshrss_client import FreshRSSManager
from scraper.xml_parser import XMLContentParser
from scraper.discord_notifier import DiscordNotifier
from config.settings import DEFAULT_SEARCH_TERMS
from loguru import logger


class FederalRegisterSearcher:
    def __init__(self, search_terms=None):
        self.search_terms = search_terms or DEFAULT_SEARCH_TERMS.copy()
        self.freshrss = FreshRSSManager()
        self.xml_parser = XMLContentParser()
        self.notifier = DiscordNotifier()

    def add_search_term(self, term):
        """Add a new search term"""
        if term not in self.search_terms:
            self.search_terms.append(term)
            logger.info(f"Added search term: {term}")
            return True
        return False

    def remove_search_term(self, term):
        """Remove a search term"""
        if term in self.search_terms:
            self.search_terms.remove(term)
            logger.info(f"Removed search term: {term}")
            return True
        return False

    def get_search_terms(self):
        """Get current search terms"""
        return self.search_terms.copy()

    def set_refresh_interval(self, seconds):
        """Set refresh interval (for future Discord integration)"""
        # This will be used later when you add Discord commands
        pass

    def process_unread_items(self):
        """Process all unread items and check for search terms - your core logic"""
        unread_items = self.freshrss.get_unread_items()

        if not unread_items:
            return []

        found_articles = []

        for item in unread_items:
            try:
                item_id = self.freshrss.extract_item_id(item)
                xml_url = self.freshrss.extract_xml_url(item)

                # Parse XML content
                xml_content = self.xml_parser.fetch_and_parse_xml(xml_url)
                if not xml_content:
                    continue

                # Search for terms
                found_terms = self.xml_parser.search_xml_content(xml_content, self.search_terms)

                if found_terms:
                    print(f"Search string found for article {item_id}!")
                    print(xml_url)

                    # Send Discord notification
                    self.notifier.send_notification(found_terms, xml_url, item_id)

                    found_articles.append({
                        'id': item_id,
                        'url': xml_url,
                        'terms': found_terms
                    })
                else:
                    print("No search string found!")

                # Mark as read
                self.freshrss.mark_as_read(item_id)

            except Exception as e:
                logger.error(f"Error processing item: {e}")
                continue

        return found_articles