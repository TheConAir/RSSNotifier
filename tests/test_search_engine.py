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
