import importlib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_guild_id_default(monkeypatch):
    monkeypatch.delenv("GUILD_ID", raising=False)
    # Prevent loading a real .env which could set GUILD_ID
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: None)
    import config.settings as settings
    importlib.reload(settings)
    assert settings.GUILD_ID == 0

