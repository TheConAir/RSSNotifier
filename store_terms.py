import json, threading
from pathlib import Path

class StoreTerms:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()   # ← reentrant
        if not self.path.exists():
            self._write([])

    def load(self) -> list[str]:
        with self._lock:
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                return []
            except Exception as e:
                print(f"[StoreTerms] load failed ({e}); returning []")
                return []

    def _write(self, terms: list[str]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(sorted(set(terms)), ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def add(self, term: str) -> list[str]:
        with self._lock:
            terms = self.load()
            if term not in terms:
                terms.append(term)
                self._write(terms)
            return terms

    def remove(self, term: str) -> list[str]:
        with self._lock:
            terms = [t for t in self.load() if t != term]
            self._write(terms)
            return terms
