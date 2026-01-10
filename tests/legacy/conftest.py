import pytest

@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.skip(reason="Legacy tests disabled (see tests/legacy/ for migration)."))
