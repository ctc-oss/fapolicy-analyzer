import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock, patch

from callee import Attrs, InstanceOf, Sequence
from fapolicy_analyzer import Changeset, Trust
from fapolicy_analyzer.redux import Action
from gi.repository import Gtk
from rx.subject import Subject
from ui.actions import (
    ADD_NOTIFICATION,
    APPLY_CHANGESETS,
    CLEAR_CHANGESETS,
    DEPLOY_ANCILLARY_TRUST,
    REQUEST_ANCILLARY_TRUST,
    SET_SYSTEM_CHECKPOINT,
    NotificationType,
)
from ui.ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from ui.store import init_store
from ui.strings import (
    ANCILLARY_TRUST_LOAD_ERROR,
    ANCILLARY_TRUSTED_FILE_MESSAGE,
    ANCILLARY_UNKNOWN_FILE_MESSAGE,
    DEPLOY_ANCILLARY_ERROR_MSG,
    DEPLOY_ANCILLARY_SUCCESSFUL_MSG,
)

from mocks import mock_System, mock_trust


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("ui.ancillary_trust_database_admin.dispatch")


@pytest.fixture
def widget(mock_dispatch, mocker):
    mocker.patch("ui.ancillary_trust_database_admin.fs.sha", return_value="abc")
    init_store(mock_System())
    return AncillaryTrustDatabaseAdmin()


@pytest.fixture
def confirm_dialog(confirm_resp, mocker):
    mock_confirm_dialog = MagicMock(
        run=MagicMock(return_value=confirm_resp),
        hide=MagicMock(),
        get_save_state=MagicMock(return_value=False),
    )
    mocker.patch(
        "ui.ancillary_trust_database_admin.ConfirmInfoDialog",
        return_value=mock_confirm_dialog,
    )

    mocker.patch(
        "ui.trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch(
        "ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    return mock_confirm_dialog


@pytest.fixture
def revert_dialog(revert_resp, mocker):
    mock_revert_dialog = MagicMock(
        run=MagicMock(return_value=revert_resp), hide=MagicMock()
    )
    mocker.patch(
        "ui.ancillary_trust_database_admin.DeployConfirmDialog.get_ref",
        return_value=mock_revert_dialog,
    )
    return mock_revert_dialog


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


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
@pytest.mark.usefixtures("revert_dialog")
def test_on_confirm_deployment(widget, confirm_dialog, mock_dispatch):
    widget.get_object("deployBtn").clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=DEPLOY_ANCILLARY_TRUST)
    )
    confirm_dialog.run.assert_called()
    confirm_dialog.hide.assert_called()


@pytest.mark.usefixtures("confirm_dialog")
@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
def test_on_deployment_w_exception(mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "ui.ancillary_trust_database_admin.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    widget = AncillaryTrustDatabaseAdmin()
    system_features_mock.on_next(
        {
            "changesets": [],
            "ancillary_trust": MagicMock(
                trust=[mock_trust()], error=None, loading=False
            ),
        }
    )
    widget.get_object("deployBtn").clicked()
    system_features_mock.on_next(
        {"changesets": [], "ancillary_trust": MagicMock(error="foo")}
    )
    mock_dispatch.assert_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=DEPLOY_ANCILLARY_ERROR_MSG),
        )
    )


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.NO])
def test_on_neg_confirm_deployment(confirm_dialog, mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "ui.ancillary_trust_database_admin.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    widget = AncillaryTrustDatabaseAdmin()
    system_features_mock.on_next(
        {
            "changesets": [],
            "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
        }
    )
    widget.get_object("deployBtn").clicked()
    confirm_dialog.run.assert_called()
    confirm_dialog.hide.assert_called()
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action) & Attrs(type=DEPLOY_ANCILLARY_TRUST)
    )


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
@pytest.mark.usefixtures("confirm_dialog", "revert_dialog")
def test_on_revert_deployment(mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "ui.ancillary_trust_database_admin.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    widget = AncillaryTrustDatabaseAdmin()
    system_features_mock.on_next(
        {
            "changesets": [],
            "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
        }
    )
    widget.get_object("deployBtn").clicked()
    system_features_mock.on_next(
        {
            "changesets": [],
            "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
        }
    )
    mock_dispatch.assert_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.SUCCESS, text=DEPLOY_ANCILLARY_SUCCESSFUL_MSG
            ),
        )
    )
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action) & Attrs(type=SET_SYSTEM_CHECKPOINT)
    )
    mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=CLEAR_CHANGESETS))


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.YES])
@pytest.mark.usefixtures("confirm_dialog", "revert_dialog")
def test_on_neg_revert_deployment(mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "ui.ancillary_trust_database_admin.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    widget = AncillaryTrustDatabaseAdmin()
    system_features_mock.on_next(
        {
            "changesets": [],
            "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
        }
    )
    widget.get_object("deployBtn").clicked()
    system_features_mock.on_next(
        {
            "changesets": [],
            "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
        }
    )
    mock_dispatch.assert_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.SUCCESS, text=DEPLOY_ANCILLARY_SUCCESSFUL_MSG
            ),
        )
    )
    mock_dispatch.assert_any_call(
        InstanceOf(Action) & Attrs(type=SET_SYSTEM_CHECKPOINT)
    )
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=CLEAR_CHANGESETS))


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


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
def test_handle_deploy_exception(widget, confirm_dialog):
    with patch("fapolicy_analyzer.System") as mock:
        mock.deploy = MagicMock(
            return_value=None, side_effect=Exception("mocked error")
        )
        widget.system = mock
        with pytest.raises(Exception) as excinfo:
            widget.on_deployBtn_clicked()
            assert excinfo.value.message == "mocked error"


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


def test_display_save_fapd_archive_dlg(widget, mocker):
    # Mock the FileChooser dlg
    mockFileChooserDlg = MagicMock()
    mockFileChooserDlg.run.return_value = Gtk.ResponseType.OK
    mockFileChooserDlg.get_filename.return_value = "/tmp/save_as_tmp.tgz"
    mocker.patch(
        "ui.ancillary_trust_database_admin.Gtk.FileChooserDialog",
        return_value=mockFileChooserDlg,
    )
    widget.display_save_fapd_archive_dlg(MagicMock())
    mockFileChooserDlg.run.assert_called()
