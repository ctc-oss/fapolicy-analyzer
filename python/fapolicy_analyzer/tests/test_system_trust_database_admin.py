import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.system_trust_database_admin import SystemTrustDatabaseAdmin
from ui.configs import Colors


@pytest.fixture
def widget():
    return SystemTrustDatabaseAdmin()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_status_markup(widget):
    assert widget._SystemTrustDatabaseAdmin__status_markup("T") == (
        "<b><u>T</u></b>/D",
        Colors.LIGHT_GREEN,
    )
    assert widget._SystemTrustDatabaseAdmin__status_markup("foo") == (
        "T/<b><u>D</u></b>",
        Colors.LIGHT_RED,
    )


def test_updates_trust_details(widget, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_database_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    mocker.patch("ui.ancillary_trust_database_admin.fs.sha", return_value="abc")
    trust = MagicMock(status="T", path="/tmp/foo", size=1, hash="abc")
    widget.on_trust_selection_changed(trust)
    widget.trustFileDetails.set_in_database_view.assert_called_with(
        "File: /tmp/foo\nSize: 1\nSHA256: abc"
    )
    widget.trustFileDetails.set_on_file_system_view.assert_called_with(
        "stat: cannot stat '/tmp/foo': No such file or directory\nSHA256: abc"
    )
    widget.trustFileDetails.set_trust_status.assert_called_with("This file is trusted.")
