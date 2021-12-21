from unittest.mock import MagicMock

import pytest
from fapolicy_analyzer.ui.operations.ui_operation import UIOperation


@pytest.fixture
def op():
    # trick it into thinking there are no abstract methods
    UIOperation.__abstractmethods__ = set()
    return UIOperation()


def test_get_text(op):
    assert op.get_text() is None


def test_get_icon(op):
    assert op.get_icon() is None


def test_run(op):
    assert op.run() is None


def test_dispose(op):
    assert op.dispose() is None


def test_calls_dispose():
    mock_cleanup = MagicMock()

    def dispose():
        mock_cleanup()

    UIOperation.__abstractmethods__ = set()
    with UIOperation() as op:
        op.dispose = dispose
    mock_cleanup.assert_called_once()
