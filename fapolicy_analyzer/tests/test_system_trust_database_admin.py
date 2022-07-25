# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock

from callee import Attrs, InstanceOf
from callee.strings import Regex
from gi.repository import Gtk
from redux import Action
from rx.subject import Subject
from fapolicy_analyzer.ui.actions import ADD_NOTIFICATION, NotificationType
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.store import init_store
from fapolicy_analyzer.ui.strings import (
    SYSTEM_TRUST_LOAD_ERROR,
    SYSTEM_TRUSTED_FILE_MESSAGE,
)
from fapolicy_analyzer.ui.system_trust_database_admin import SystemTrustDatabaseAdmin

from mocks import mock_System, mock_trust


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.system_trust_database_admin.dispatch")


@pytest.fixture()
def mock_system_feature(mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.system_trust_database_admin.get_system_feature",
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
        "<b><u>T</u></b> / D",
        Colors.LIGHT_GREEN,
    )
    assert widget._SystemTrustDatabaseAdmin__status_markup("foo") == (
        "T / <b><u>D</u></b>",
        Colors.LIGHT_RED,
        Colors.WHITE,
    )


def test_updates_trust_details(widget, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_database_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    mocker.patch(
        "fapolicy_analyzer.ui.ancillary_trust_database_admin.fs.sha", return_value="abc"
    )
    trust = [MagicMock(status="T", path="/tmp/foo", size=1, hash="abc")]
    widget.on_trust_selection_changed(trust)
    widget.trustFileDetails.set_in_database_view.assert_called_with(
        "File: /tmp/foo\nSize: 1\nSHA256: abc"
    )
    widget.trustFileDetails.set_on_file_system_view.assert_called_with(
        Regex(r"stat: cannot statx? '/tmp/foo': No such file or directory\nSHA256: abc")
    )
    widget.trustFileDetails.set_trust_status.assert_called_with(
        SYSTEM_TRUSTED_FILE_MESSAGE
    )


def test_disables_add_button(widget):
    addBtn = widget.get_object("addBtn")
    addBtn.set_sensitive(True)
    assert addBtn.get_sensitive()
    widget.on_trust_selection_changed(None)
    assert not addBtn.get_sensitive()


def test_fires_file_added_to_ancillary_trust(widget):
    handler = MagicMock()
    widget.file_added_to_ancillary_trust += handler
    widget.selectedFiles = [MagicMock(path="foo")]
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
        {
            "changesets": [],
            "system_trust": MagicMock(error=None, trust=mockTrust, loading=False),
        }
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
            payload=Attrs(type=NotificationType.ERROR, text=SYSTEM_TRUST_LOAD_ERROR),
            type=ADD_NOTIFICATION,
        )
    )
