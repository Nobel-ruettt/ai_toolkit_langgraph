import importlib


def test_import():
    pkg = importlib.import_module("ai_toolkit")
    assert hasattr(pkg, "__version__")
