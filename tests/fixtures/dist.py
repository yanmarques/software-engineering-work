import pytest

import sys


@pytest.fixture
def with_bundled(monkeypatch):
    def wrapper(path):
        monkeypatch.setattr(sys, 'frozen', True, raising=False)
        monkeypatch.setattr(sys, '_MEIPASS', path, raising=False)

    return wrapper
