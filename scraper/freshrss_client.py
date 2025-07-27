from freshrss_api import FreshRSSAPI
from config.settings import FRESHRSS_HOST, FRESHRSS_USERNAME, FRESHRSS_PASSWORD
from loguru import logger
import sys

# Filter out the set_mark logging noise (your original fix)
logger.remove()
logger.add(sys.stderr, filter=lambda rec: rec["function"] != "set_mark")


class FreshRSSManager:
    def __init__(self):
        self.client = FreshRSSAPI(
            host=FRESHRSS_HOST,
            username=FRESHRSS_USERNAME,
            password=FRESHRSS_PASSWORD,
            verify_ssl=False,
            verbose=False
        )

    def get_unread_items(self):
        """Fetch all unread items from FreshRSS"""
        try:
            return self.client.get_unreads()
        except Exception as e:
            logger.error(f"Failed to get unread items: {e}")
            return []

    def get_all_items(self):
        """Fetch all items from FreshRSS"""
        try:
            return self.client.get_items_from_dates(since="1970-01-01")
        except Exception as e:
            logger.error(f"Failed to get all items: {e}")
            return []

    def mark_as_read(self, item_id):
        """Mark an item as read"""
        try:
            self.client.set_mark(as_="read", id=item_id)
            return True
        except Exception as e:
            logger.error(f"Failed to mark item {item_id} as read: {e}")
            return False

    def extract_item_id(self, item):
        """Extract the ID from an item object"""
        return str(item).split("id=")[1].split(",")[0]

    def extract_xml_url(self, item):
        """Extract the XML URL from an item object"""
        return str(item).split(r'<br>\n <a href="')[1].split('">XML</a>')[0]
