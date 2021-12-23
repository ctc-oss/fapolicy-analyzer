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

import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

import gi
import pytest
from callee import InstanceOf
from callee.attributes import Attrs
from callee.collections import Sequence
from fapolicy_analyzer import Changeset, Trust
from redux import Action
from rx.subject import Subject
from ui.actions import (
    ADD_NOTIFICATION,
    APPLY_CHANGESETS,
    REQUEST_ANCILLARY_TRUST,
    NotificationType,
)
from ui.ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from ui.store import init_store
from ui.strings import (
    ANCILLARY_TRUST_LOAD_ERROR,
    ANCILLARY_TRUSTED_FILE_MESSAGE,
    ANCILLARY_UNKNOWN_FILE_MESSAGE,
)

from mocks import mock_System

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("ui.ancillary_trust_database_admin.dispatch")


@pytest.fixture
def widget(mock_dispatch, mocker):
    mocker.patch("ui.ancillary_trust_database_admin.fs.sha", return_value="abc")
    init_store(mock_System())
    return AncillaryTrustDatabaseAdmin()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_updates_trust_details(widget, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_database_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    mocker.patch(
        "ui.ancillary_trust_database_admin.fs.stat", return_value="stat for foo file"
    )
    trust = MagicMock(status="T", path="/tmp/foo", size=1, hash="abc", spec=Trust)
    widget.on_trust_selection_changed(trust)
    widget.trustFileDetails.set_in_database_view.assert_called_with(
        "File: /tmp/foo\nSize: 1\nSHA256: abc"
    )
    widget.trustFileDetails.set_on_file_system_view.assert_called_with(
        "stat for foo file\nSHA256: abc"
    )
    widget.trustFileDetails.set_trust_status.assert_called_with(
        ANCILLARY_TRUSTED_FILE_MESSAGE
    )


def test_updates_trust_details_for_deleted_files(widget, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_database_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    mocker.patch(
        "ui.ancillary_trust_database_admin.fs.stat", return_value="stat for foo file"
    )
    trust = MagicMock(path="/tmp/foo")
    widget.on_trust_selection_changed(trust)
    widget.trustFileDetails.set_in_database_view.assert_not_called()
    widget.trustFileDetails.set_on_file_system_view.assert_called_with(
        "stat for foo file\nSHA256: abc"
    )
    widget.trustFileDetails.set_trust_status.assert_called_with(
        ANCILLARY_UNKNOWN_FILE_MESSAGE
    )


def test_clears_trust_details(widget, mocker):
    mocker.patch.object(widget.trustFileDetails, "clear")
    trustBtn = widget.get_object("trustBtn")
    untrustBtn = widget.get_object("untrustBtn")
    trustBtn.set_sensitive(True)
    untrustBtn.set_sensitive(True)
    widget.on_trust_selection_changed(None)
    assert not trustBtn.get_sensitive()
    assert not untrustBtn.get_sensitive()
    widget.trustFileDetails.clear.assert_called()


def test_add_trusted_files(widget, mock_dispatch):
    widget.add_trusted_files("foo")
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=APPLY_CHANGESETS, payload=Sequence(of=InstanceOf(Changeset)))
    )


def test_delete_trusted_files(widget, mock_dispatch):
    widget.add_trusted_files("foo")
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=APPLY_CHANGESETS,
            payload=Sequence(of=InstanceOf(Changeset)),
        )
    )


def test_on_trustBtn_clicked(widget, mock_dispatch, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_database_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    mocker.patch(
        "ui.ancillary_trust_database_admin.fs.stat", return_value="stat for foo file"
    )
    trust = MagicMock(path="/tmp/foo")
    widget.on_trust_selection_changed(trust)
    widget.get_object("trustBtn").clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=APPLY_CHANGESETS,
            payload=Sequence(of=InstanceOf(Changeset)),
        )
    )


def test_on_trustBtn_clicked_empty(widget, mock_dispatch):
    widget.get_object("trustBtn").clicked()
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action)
        & Attrs(
            type=APPLY_CHANGESETS,
            payload=Sequence(of=InstanceOf(Changeset)),
        )
    )


def test_on_untrustBtn_clicked(widget, mock_dispatch, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_database_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    mocker.patch(
        "ui.ancillary_trust_database_admin.fs.stat", return_value="stat for foo file"
    )
    trust = MagicMock(path="/tmp/foo")
    widget.on_trust_selection_changed(trust)
    widget.get_object("untrustBtn").clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=APPLY_CHANGESETS,
            payload=Sequence(of=InstanceOf(Changeset)),
        )
    )


def test_on_untrustBtn_clicked_empty(widget, mock_dispatch):
    widget.get_object("untrustBtn").clicked()
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action)
        & Attrs(
            type=APPLY_CHANGESETS,
            payload=Sequence(of=InstanceOf(Changeset)),
        )
    )


def test_on_file_added(widget, mock_dispatch):
    widget.on_files_added("foo")
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=APPLY_CHANGESETS, payload=Sequence(of=InstanceOf(Changeset)))
    )


def test_on_file_added_empty(widget, mock_dispatch):
    widget.on_files_added(None)
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action)
        & Attrs(type=APPLY_CHANGESETS, payload=Sequence(of=InstanceOf(Changeset)))
    )


def test_on_file_deleted(widget, mock_dispatch):
    widget.on_files_deleted("foo")
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=APPLY_CHANGESETS, payload=Sequence(of=InstanceOf(Changeset)))
    )


def test_on_file_deleted_empty(widget, mock_dispatch):
    widget.on_files_deleted(None)
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action)
        & Attrs(type=APPLY_CHANGESETS, payload=Sequence(of=InstanceOf(Changeset)))
    )


def test_reloads_trust_w_changeset_change(mock_dispatch, mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "ui.ancillary_trust_database_admin.get_system_feature",
        return_value=mockSystemFeature,
    )
    mockSystemFeature.on_next({"changesets": []})
    init_store(mock_System())
    widget = AncillaryTrustDatabaseAdmin()
    mockTrustListSetChangeset = mocker.patch.object(
        widget.trustFileList, "set_changesets"
    )

    changesets = [MagicMock()]
    mockSystemFeature.on_next(
        {"changesets": changesets, "ancillary_trust": MagicMock(error=None)}
    )
    mockTrustListSetChangeset.assert_called_with(changesets)
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=REQUEST_ANCILLARY_TRUST)
    )


def test_load_trust(mocker):
    mockChangeset = MagicMock(spec=Changeset)
    mockSystemFeature = Subject()
    mocker.patch(
        "ui.ancillary_trust_database_admin.get_system_feature",
        return_value=mockSystemFeature,
    )
    init_store(mock_System())
    widget = AncillaryTrustDatabaseAdmin()
    mockLoadList = mocker.patch.object(widget.trustFileList, "load_trust")
    mockSystemFeature.on_next(
        {
            "changesets": [mockChangeset],
            "ancillary_trust": MagicMock(error=False),
        }
    )

    mockSystemFeature.on_next(
        {
            "changesets": [mockChangeset],
            "ancillary_trust": MagicMock(error=False, loading=False, trust="foo"),
        }
    )
    mockLoadList.assert_called_once_with("foo")


def test_load_trust_w_exception(mock_dispatch, mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "ui.ancillary_trust_database_admin.get_system_feature",
        return_value=mockSystemFeature,
    )
    mockSystemFeature.on_next({"changesets": []})
    init_store(mock_System())
    AncillaryTrustDatabaseAdmin()

    mockSystemFeature.on_next(
        {"changesets": [], "ancillary_trust": MagicMock(loading=False, error="foo")}
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=ANCILLARY_TRUST_LOAD_ERROR),
        )
    )
