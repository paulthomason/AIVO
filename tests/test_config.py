import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

import config  # noqa: E402


def test_get_env_int(monkeypatch):
    monkeypatch.setenv('TEST_INT', '123')
    assert config.get_env_int('TEST_INT', 10) == 123
    monkeypatch.setenv('TEST_INT', 'abc')
    assert config.get_env_int('TEST_INT', 10) == 10
    monkeypatch.delenv('TEST_INT', raising=False)
    assert config.get_env_int('TEST_INT', 10) == 10


def test_get_env_bool(monkeypatch):
    monkeypatch.setenv('TEST_BOOL', '1')
    assert config.get_env_bool('TEST_BOOL') is True
    monkeypatch.setenv('TEST_BOOL', 'false')
    assert config.get_env_bool('TEST_BOOL') is False
    monkeypatch.delenv('TEST_BOOL', raising=False)
    assert config.get_env_bool('TEST_BOOL') is False
