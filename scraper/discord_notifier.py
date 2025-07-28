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