import json
import importlib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))


def create_searcher(tmp_path, monkeypatch):
    monkeypatch.setenv("GUILD_ID", "1")
    import scraper.search_engine as se
    importlib.reload(se)
    # replace heavy dependencies with stubs
    monkeypatch.setattr(se, "FreshRSSManager", lambda: None)
    monkeypatch.setattr(se, "XMLContentParser", lambda: None)
    monkeypatch.setattr(se, "DiscordNotifier", lambda: None)
    searcher = se.FederalRegisterSearcher()
    searcher._store = se.StoreTerms(tmp_path / "terms.json")
    searcher.search_terms = []
    return searcher


def create_searcher_with_items(tmp_path, monkeypatch, items, xml_map):
    """Return a FederalRegisterSearcher instance with stubbed dependencies."""
    monkeypatch.setenv("GUILD_ID", "1")
    import scraper.search_engine as se
    importlib.reload(se)

    class FRStub:
        def __init__(self):
            pass

        def get_all_items(self):
            return items

        def get_unread_items(self):
            return items

        def extract_item_id(self, item):
            return item.id

        def extract_xml_url(self, item):
            return item.url

        def mark_as_read(self, item_id):
            raise AssertionError("mark_as_read should not be called during rescan")

    class XMLStub:
        def fetch_and_parse_xml(self, url):
            return xml_map.get(url, "")

        def search_xml_content(self, xml_content, terms):
            low = xml_content.lower()
            return [t for t in terms if t.lower() in low]

    class NotifyStub:
        def __init__(self, webhook_url=None):
            pass

        def send_notification(self, *a, **kw):
            raise AssertionError("send_notification should not be called during rescan")

    monkeypatch.setattr(se, "FreshRSSManager", FRStub)
    monkeypatch.setattr(se, "XMLContentParser", XMLStub)
    monkeypatch.setattr(se, "DiscordNotifier", NotifyStub)

    searcher = se.FederalRegisterSearcher()
    searcher._store = se.StoreTerms(tmp_path / "terms.json")
    searcher.search_terms = ["alpha", "beta"]
    return searcher


def test_add_search_term(monkeypatch, tmp_path):
    searcher = create_searcher(tmp_path, monkeypatch)

    assert searcher.add_search_term("alpha") is True
    assert searcher.get_search_terms() == ["alpha"]
    # file persisted
    data = json.loads((tmp_path / "terms.json").read_text())
    assert data == ["alpha"]

    # duplicate
    assert searcher.add_search_term("alpha") is False
    assert searcher.get_search_terms() == ["alpha"]

    # blank value
    assert searcher.add_search_term("") is False
    assert searcher.add_search_term("   ") is False
    assert searcher.add_search_term(None) is False


def test_process_items_rescan(monkeypatch, tmp_path):
    class Item:
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)

    fr_item = Item(feed_id=2, id="a", url="http://example.com/a.xml")
    sec_item = Item(feed_id=3, id="b", url="http://example.com/b", title="Beta update")

    xml_map = {"http://example.com/a.xml": "alpha beta content"}

    searcher = create_searcher_with_items(tmp_path, monkeypatch, [fr_item, sec_item], xml_map)

    results = searcher.process_items(True)

    assert results == [
        {"id": "a", "url": "http://example.com/a.xml", "terms": ["alpha", "beta"]},
        {"id": "b", "url": "http://example.com/b", "terms": ["beta"]},
    ]
