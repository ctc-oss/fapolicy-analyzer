import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from mocks import mock_System
from helpers import refresh_gui
from ui.system_trust_database_admin import SystemTrustDatabaseAdmin


@pytest.fixture
def widget(mocker):
    mocker.patch("ui.system_trust_database_admin.System", return_value=mock_System())
    widget = SystemTrustDatabaseAdmin()
    refresh_gui(0.1)
    return widget


def test_creates_widget(widget):
    assert type(widget.get_content()) is Gtk.Box


def test_status_markup(widget):
    assert widget._SystemTrustDatabaseAdmin__status_markup("T") == (
        "<b><u>T</u></b>",
        "light green",
    )
    assert widget._SystemTrustDatabaseAdmin__status_markup("foo") == ("T", "light red")


def test_updates_trust_details(widget, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_databae_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    mocker.patch("ui.ancillary_trust_database_admin.fs.sha", return_value="abc")
    trust = MagicMock(status="T", path="/tmp/foo", size=1, hash="abc")
    widget.on_file_selection_change(trust)
    widget.trustFileDetails.set_in_databae_view.assert_called_with(
        "File: /tmp/foo\nSize: 1\nSHA256: abc"
    )
    widget.trustFileDetails.set_on_file_system_view.assert_called_with(
        "stat: cannot stat '/tmp/foo': No such file or directory\nSHA256: abc"
    )
    widget.trustFileDetails.set_trust_status.assert_called_with("This file is trusted.")
