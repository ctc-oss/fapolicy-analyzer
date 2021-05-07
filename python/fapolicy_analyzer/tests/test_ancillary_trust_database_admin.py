import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
import tempfile
from ui.ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from ui.configs import Colors
from ui.state_manager import stateManager


@pytest.fixture
def mock_util(mocker):
    mocker.patch("ui.ancillary_trust_database_admin.fs.sha", return_value="abc")


@pytest.fixture
def widget(mock_util):
    return AncillaryTrustDatabaseAdmin()


@pytest.fixture
def state():
    stateManager.del_changeset_q()
    yield stateManager
    stateManager.del_changeset_q()


def test_creates_widget(widget):
    assert type(widget.get_content()) is Gtk.Box


def test_status_markup(widget):
    assert widget._AncillaryTrustDatabaseAdmin__status_markup("T") == (
        "<b><u>T</u></b>/D",
        Colors.LIGHT_GREEN,
    )
    assert widget._AncillaryTrustDatabaseAdmin__status_markup("D") == (
        "T/<b><u>D</u></b>",
        Colors.LIGHT_RED,
    )
    assert widget._AncillaryTrustDatabaseAdmin__status_markup("foo") == (
        "T/D",
        Colors.LIGHT_YELLOW,
    )


def test_updates_trust_details(widget, mocker):
    mocker.patch.object(widget.trustFileDetails, "set_in_databae_view")
    mocker.patch.object(widget.trustFileDetails, "set_on_file_system_view")
    mocker.patch.object(widget.trustFileDetails, "set_trust_status")
    trust = MagicMock(status="T", path="/tmp/foo", size=1, hash="abc")
    widget.on_file_selection_change(trust)
    widget.trustFileDetails.set_in_databae_view.assert_called_with(
        "File: /tmp/foo\nSize: 1\nSHA256: abc"
    )
    widget.trustFileDetails.set_on_file_system_view.assert_called_with(
        "stat: cannot stat '/tmp/foo': No such file or directory\nSHA256: abc"
    )
    widget.trustFileDetails.set_trust_status.assert_called_with("This file is trusted.")


def test_on_confirm_deployment(widget, mocker):
    parent = Gtk.Window()
    parent.add(widget.get_content())
    mock_confirm_dialog = MagicMock(
        run=MagicMock(return_value=Gtk.ResponseType.YES), hide=MagicMock()
    )
    mock_deploy_dialog = MagicMock(run=MagicMock(), hide=MagicMock())
    mocker.patch(
        "ui.ancillary_trust_database_admin.ConfirmDialog.get_content",
        return_value=mock_confirm_dialog,
    )
    mocker.patch(
        "ui.ancillary_trust_database_admin.DeployConfirmDialog.get_content",
        return_value=mock_deploy_dialog,
    )

    widget.on_deployBtn_clicked()
    mock_confirm_dialog.run.assert_called()
    mock_confirm_dialog.hide.assert_called()
    mock_deploy_dialog.run.assert_called()
    mock_deploy_dialog.hide.assert_called()


def test_on_neg_confirm_deployment(widget, mocker):
    parent = Gtk.Window()
    parent.add(widget.get_content())
    mock_confirm_dialog = MagicMock(
        run=MagicMock(return_value=Gtk.ResponseType.NO), hide=MagicMock()
    )
    mock_deploy_dialog = MagicMock(run=MagicMock())
    mocker.patch(
        "ui.ancillary_trust_database_admin.ConfirmDialog.get_content",
        return_value=mock_confirm_dialog,
    )
    mocker.patch(
        "ui.ancillary_trust_database_admin.DeployConfirmDialog.get_content",
        return_value=mock_deploy_dialog,
    )

    widget.on_deployBtn_clicked()
    mock_confirm_dialog.run.assert_called()
    mock_confirm_dialog.hide.assert_called()
    mock_deploy_dialog.run.assert_not_called()


def test_add_trusted_files(widget, state):
    assert len(state.get_changeset_q()) == 0
    tmpFile = tempfile.NamedTemporaryFile()
    widget.add_trusted_files(tmpFile.name)
    assert len(state.get_changeset_q()) == 1
    changeset = state.next_changeset_q()
    assert changeset.len() == 1


def test_delete_trusted_files(widget, state):
    assert len(state.get_changeset_q()) == 0
    tmpFile = tempfile.NamedTemporaryFile()
    widget.delete_trusted_files(tmpFile.name)
    assert len(state.get_changeset_q()) == 1
    changeset = state.next_changeset_q()
    assert changeset.len() == 1


def test_on_trustBtn_clicked(widget, state):
    assert len(state.get_changeset_q()) == 0
    tmpFile = tempfile.NamedTemporaryFile()
    tmpFile.seek(0, 2)
    trust = MagicMock(status="T", path=tmpFile.name, size=tmpFile.tell(), hash="abc")
    widget.on_file_selection_change(trust)
    widget.on_trustBtn_clicked()
    assert len(state.get_changeset_q()) == 1


def test_on_trustBtn_clicked_empty(widget, state):
    assert len(state.get_changeset_q()) == 0
    widget.on_trustBtn_clicked()
    assert len(state.get_changeset_q()) == 0


def test_on_untrustBtn_clicked(widget, state):
    assert len(state.get_changeset_q()) == 0
    tmpFile = tempfile.NamedTemporaryFile()
    tmpFile.seek(0, 2)
    trust = MagicMock(status="T", path=tmpFile.name, size=tmpFile.tell(), hash="abc")
    widget.on_file_selection_change(trust)
    widget.on_untrustBtn_clicked()
    assert len(state.get_changeset_q()) == 1


def test_on_untrustBtn_clicked_empty(widget, state):
    assert len(state.get_changeset_q()) == 0
    widget.on_untrustBtn_clicked()
    assert len(state.get_changeset_q()) == 0


def test_on_file_added(widget, state):
    assert len(state.get_changeset_q()) == 0
    tmpFile = tempfile.NamedTemporaryFile()
    widget.trustFileList.files_added([tmpFile.name])
    assert len(state.get_changeset_q()) == 1


def test_on_file_added_empty(widget, state):
    assert len(state.get_changeset_q()) == 0
    widget.on_files_added(None)
    assert len(state.get_changeset_q()) == 0
