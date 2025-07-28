import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from store_terms import StoreTerms


def test_add_and_remove(tmp_path):
    path = tmp_path / "terms.json"
    store = StoreTerms(path)

    assert store.load() == []

    # add first term
    terms = store.add("alpha")
    assert terms == ["alpha"]
    assert json.loads(path.read_text()) == ["alpha"]

    # add second term and check sorting
    terms = store.add("beta")
    assert terms == ["alpha", "beta"] or terms == ["beta", "alpha"]
    # load returns sorted
    assert store.load() == ["alpha", "beta"]

    # adding duplicate does nothing
    terms = store.add("beta")
    assert terms == ["alpha", "beta"]

    # remove a term
    terms = store.remove("alpha")
    assert terms == ["beta"]
    assert store.load() == ["beta"]

    # removing missing term keeps list
    terms = store.remove("missing")
    assert terms == ["beta"]
