import importlib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_send_notification(monkeypatch):
    captured = {}

    class Response:
        status_code = 200

    class WebhookStub:
        def __init__(self, url, content):
            captured['url'] = url
            captured['content'] = content
        def execute(self):
            return Response()

    monkeypatch.setattr('scraper.discord_notifier.DiscordWebhook', WebhookStub)

    from scraper.discord_notifier import DiscordNotifier
    notifier = DiscordNotifier('hook')
    notifier.send_notification(['alpha'], 'http://example.com', '123')

    assert captured['url'] == 'hook'
    assert 'alpha' in captured['content']
    assert 'http://example.com' in captured['content']

