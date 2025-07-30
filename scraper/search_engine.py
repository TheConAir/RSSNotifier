from scraper.freshrss_client import FreshRSSManager
from scraper.xml_parser import XMLContentParser
from scraper.discord_notifier import DiscordNotifier
from config.settings import DEFAULT_SEARCH_TERMS
from loguru import logger
from pathlib import Path
from store_terms import StoreTerms
import re



class FederalRegisterSearcher:
    def __init__(self, search_terms=None):
        self.freshrss = FreshRSSManager()
        self.xml_parser = XMLContentParser()
        self.notifier = DiscordNotifier()
        self._store = StoreTerms(Path("data/search_terms.json"))

        persisted = self._store.load()

        if search_terms is not None:
            self.search_terms = list(search_terms)
        elif persisted:
            self.search_terms = persisted
        else:
            self.search_terms = list(DEFAULT_SEARCH_TERMS)

    def add_search_term(self, term):
        term = (term or "").strip()
        if not term:
            return False
        if term not in self.search_terms:
            self.search_terms = self._store.add(term)  # writes file
            logger.info(f"Added search term: {term}")
            return True
        return False

    def remove_search_term(self, term):
        term = (term or "").strip()
        if not term:
            return False
        if term in self.search_terms:
            self.search_terms = self._store.remove(term)  # writes file
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

    def _find_terms_in_text(self, text: str, terms) -> list[str]:
        """Return the search terms that appear in text (case-insensitive)."""
        if not text:
            return []
        low = text.lower()
        return [t for t in terms if t.lower() in low]

    def _extract_8k_info(self, title: str):
        """Attempt to extract company and context from an 8-K title."""
        if not title:
            return ("Unknown", "")
        company = title
        context = title
        m = re.split(r'form\s*8-k', title, flags=re.IGNORECASE)
        if m:
            company = m[0].strip(" -") or company
        return (company, context)

    def process_items(self, rescan):
        """Process all unread items and check for search terms - your core logic"""
        if rescan:
            unread_items = self.freshrss.get_all_items()
        else:
            unread_items = self.freshrss.get_unread_items()

        if not unread_items:
            return []

        found_articles = []

        for item in unread_items:
            feed_id = item.feed_id
            if feed_id == 2:
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
                        logger.info(
                            f"Search string found for Federal Register article {item_id}!"
                        )
                        logger.info(xml_url)

                        # Send Discord notification
                        if not rescan:
                            self.notifier.send_notification(found_terms, xml_url, item_id)

                        found_articles.append({
                            'id': item_id,
                            'url': xml_url,
                            'terms': found_terms
                        })

                    # Mark as read
                    if not rescan:
                        self.freshrss.mark_as_read(item_id)

                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    continue
            elif feed_id == 3:
                try:
                    url = item.url
                    item_id = item.id
                    title = item.title or ""

                    # Always look for 8-K filings
                    if "8-k" in title.lower():
                        company, context = self._extract_8k_info(title)
                        logger.info(f"8-K filing found for SEC article {item_id}!")
                        logger.info(url)
                        if not rescan:
                            self.notifier.send_8k_notification(company, context, url, item_id)
                        found_articles.append({
                            'id': item_id,
                            'url': url,
                            'terms': ['8-K'],
                            'company': company,
                            'context': context,
                        })

                    # Match against the SEC item title, excluding the 8-K form which is handled separately
                    found_terms = [
                        t
                        for t in self._find_terms_in_text(title, self.search_terms)
                        if t.lower() != "8-k"
                    ]

                    if found_terms:
                        logger.info(
                            f"Search string found for SEC article {item_id}!"
                        )
                        logger.info(url)

                        # Send Discord notification
                        if not rescan:
                            self.notifier.send_notification(found_terms, url, item_id)

                        found_articles.append({
                            'id': item_id,
                            'url': url,
                            'terms': found_terms
                        })

                    # Mark as read
                    if not rescan:
                        self.freshrss.mark_as_read(item_id)

                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    continue

        return found_articles
