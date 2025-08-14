from core.config import settings
from core.version import __version__

def test_config_and_version():
    assert settings.env in {"dev", "prod", "test"}
    assert isinstance(__version__, str) and len(__version__) > 0
