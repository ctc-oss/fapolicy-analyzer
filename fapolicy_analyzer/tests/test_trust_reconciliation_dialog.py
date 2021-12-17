# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock

from gi.repository import Gtk
from ui.strings import (
    ANCILLARY_DISCREPANCY_FILE_MESSAGE,
    ANCILLARY_TRUSTED_FILE_MESSAGE,
    ANCILLARY_UNKNOWN_FILE_MESSAGE,
    SYSTEM_DISCREPANCY_FILE_MESSAGE,
    SYSTEM_TRUSTED_FILE_MESSAGE,
    SYSTEM_UNKNOWN_FILE_MESSAGE,
    UNKNOWN_FILE_MESSAGE,
)
from ui.trust_reconciliation_dialog import TrustReconciliationDialog


@pytest.fixture
def patch(mocker):
    mocker.patch("ui.trust_reconciliation_dialog.fs.sha", return_value="abc")


@pytest.fixture
def mockTrustDetailsWidget(mocker):
    mock = MagicMock(
        set_in_database_view=MagicMock(),
        set_on_file_system_view=MagicMock(),
        set_trust_status=MagicMock(),
        get_ref=MagicMock(return_value=Gtk.Box()),
    )
    mocker.patch(
        "ui.trust_reconciliation_dialog.TrustFileDetails",
        return_value=mock,
    )
    return mock


@pytest.mark.usefixtures("patch")
def test_creates_widget():
    widget = TrustReconciliationDialog(MagicMock())
    assert type(widget.get_ref()) is Gtk.Dialog


@pytest.mark.usefixtures("patch")
def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = TrustReconciliationDialog(MagicMock(), parent=parent)
    assert widget.get_ref().get_transient_for() == parent


@pytest.mark.usefixtures("patch")
def test_shows_in_database_data(mockTrustDetailsWidget):
    mockTrustObj = MagicMock(file="foo")
    mockDatabaseTrust = MagicMock(size=1, hash="abc", status="T")
    TrustReconciliationDialog(mockTrustObj, databaseTrust=mockDatabaseTrust)
    mockTrustDetailsWidget.set_in_database_view.assert_called_once_with(
        """FILE: foo
SIZE: 1
SHA256: abc"""
    )


@pytest.mark.usefixtures("patch")
def test_handles_empty_database_data(mockTrustDetailsWidget):
    mockTrustObj = MagicMock(file="foo")
    TrustReconciliationDialog(mockTrustObj)
    mockTrustDetailsWidget.set_in_database_view.assert_called_once_with(
        """FILE: foo
SIZE: Unknown
SHA256: Unknown"""
    )


@pytest.mark.usefixtures("patch")
def test_shows_on_system_data(mockTrustDetailsWidget, mocker):
    mockTrustObj = MagicMock(file="foo")
    mockDatabaseTrust = MagicMock(size=1, hash="abc", status="T")
    mocker.patch(
        "ui.trust_reconciliation_dialog.fs.stat", return_value="foo file stats"
    )
    TrustReconciliationDialog(mockTrustObj, databaseTrust=mockDatabaseTrust)
    mockTrustDetailsWidget.set_on_file_system_view.assert_called_once_with(
        """foo file stats
SHA256: abc"""
    )


@pytest.mark.usefixtures("patch")
@pytest.mark.parametrize(
    "trust, status, message",
    [
        ("st", "t", SYSTEM_TRUSTED_FILE_MESSAGE),
        ("st", "d", SYSTEM_DISCREPANCY_FILE_MESSAGE),
        ("st", "foo", SYSTEM_UNKNOWN_FILE_MESSAGE),
        ("at", "t", ANCILLARY_TRUSTED_FILE_MESSAGE),
        ("at", "d", ANCILLARY_DISCREPANCY_FILE_MESSAGE),
        ("at", "foo", ANCILLARY_UNKNOWN_FILE_MESSAGE),
        ("u", "foo", UNKNOWN_FILE_MESSAGE),
        ("baz", "foo", UNKNOWN_FILE_MESSAGE),
    ],
)
def test_shows_trust_message(mockTrustDetailsWidget, trust, status, message):
    mockTrustObj = MagicMock(trust=trust)
    mockDatabaseTrust = MagicMock(status=status)
    TrustReconciliationDialog(mockTrustObj, databaseTrust=mockDatabaseTrust)
    mockTrustDetailsWidget.set_trust_status.assert_called_once_with(message)


@pytest.mark.usefixtures("patch")
@pytest.mark.parametrize(
    "trust, status, visible",
    [
        ("st", "t", False),
        ("st", "d", True),
        ("st", "foo", True),
        ("at", "t", False),
        ("at", "d", True),
        ("at", "foo", True),
        ("u", "foo", True),
        ("baz", "foo", True),
    ],
)
def test_sets_trust_button_visiblity(trust, status, visible):
    mockTrustObj = MagicMock(trust=trust)
    mockDatabaseTrust = MagicMock(status=status)
    widget = TrustReconciliationDialog(mockTrustObj, databaseTrust=mockDatabaseTrust)
    assert widget.get_object("trustBtn").get_visible() == visible


@pytest.mark.usefixtures("patch")
@pytest.mark.parametrize(
    "trust, status, visible",
    [
        ("st", "t", False),
        ("st", "d", False),
        ("st", "foo", False),
        ("at", "t", True),
        ("at", "d", False),
        ("at", "foo", False),
        ("u", "foo", False),
        ("baz", "foo", False),
    ],
)
def test_sets_untrust_button_visiblity(trust, status, visible):
    mockTrustObj = MagicMock(trust=trust)
    mockDatabaseTrust = MagicMock(status=status)
    widget = TrustReconciliationDialog(mockTrustObj, databaseTrust=mockDatabaseTrust)
    assert widget.get_object("untrustBtn").get_visible() == visible
