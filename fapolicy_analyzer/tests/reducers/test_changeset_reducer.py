import context  # noqa: F401
from unittest.mock import MagicMock
from ui.reducers.changeset_reducer import handle_add_changesets, handle_clear_changesets


def test_handle_add_changesets():
    result = handle_add_changesets([], MagicMock(payload=["foo"]))
    assert list(result) == ["foo"]


def test_handle_clear_changesets():
    result = handle_clear_changesets(["foo", "foo2"], MagicMock())
    assert result == []
