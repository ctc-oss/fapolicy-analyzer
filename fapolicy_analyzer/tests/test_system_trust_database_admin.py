import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from callee import InstanceOf, Attrs
from callee.strings import Regex
from gi.repository import Gtk
from mocks import mock_System, mock_trust
from redux import Action
from rx.subject import Subject
from unittest.mock import MagicMock
from ui.actions import ADD_NOTIFICATION, NotificationType
from ui.configs import Colors
from ui.strings import SYSTEM_TRUST_LOAD_ERROR
from ui.store import init_store
from ui.system_trust_database_admin import SystemTrustDatabaseAdmin


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("ui.system_trust_database_admin.dispatch")


@pytest.fixture()
def mock_system_feature(mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "ui.system_trust_database_admin.get_system_feature",
        return_value=mockSystemFeature,
    )
    yield mockSystemFeature
    mockSystemFeature.on_completed()


@pytest.fixture
def widget(mock_dispatch):
    init_store(mock_System())
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
        Regex(r"stat: cannot statx? '/tmp/foo': No such file or directory\nSHA256: abc")
    )
    widget.trustFileDetails.set_trust_status.assert_called_with("This file is trusted.")


def test_disables_add_button(widget):
    addBtn = widget.get_object("addBtn")
    addBtn.set_sensitive(True)
    assert addBtn.get_sensitive()
    widget.on_trust_selection_changed(None)
    assert not addBtn.get_sensitive()


def test_fires_file_added_to_ancillary_trust(widget):
    handler = MagicMock()
    widget.file_added_to_ancillary_trust += handler
    widget.selectedFile = MagicMock(path="foo")
    addBtn = widget.get_object("addBtn")
    addBtn.clicked()
    handler.assert_called_with("foo")


def test_load_trust(mock_dispatch, mock_system_feature, mocker):
    mock_system_feature.on_next({"changesets": []})
    init_store(mock_System())
    widget = SystemTrustDatabaseAdmin()
    mockTrustListLoad = mocker.patch.object(widget.trustFileList, "load_trust")

    mockTrust = [mock_trust()]
    mock_system_feature.on_next(
        {"changesets": [], "system_trust": MagicMock(error=None, trust=mockTrust)}
    )
    mockTrustListLoad.assert_called_with(mockTrust)


def test_load_trust_w_exception(mock_dispatch, mock_system_feature):
    mock_system_feature.on_next({"changesets": []})
    init_store(mock_System())
    SystemTrustDatabaseAdmin()

    mock_system_feature.on_next(
        {"changesets": [], "system_trust": MagicMock(loading=False, error="foo")}
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=SYSTEM_TRUST_LOAD_ERROR),
        )
    )
