import context  # noqa: F401
import pytest
import tempfile
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock, patch
from ui.ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from ui.configs import Colors
from ui.state_manager import stateManager


@pytest.fixture
def widget(mocker):
    mocker.patch("ui.ancillary_trust_database_admin.fs.sha", return_value="abc")
    return AncillaryTrustDatabaseAdmin()


@pytest.fixture
def confirm_dialog(confirm_resp, mocker):
    mock_confirm_dialog = MagicMock(
        run=MagicMock(return_value=confirm_resp), hide=MagicMock()
    )
    mocker.patch(
        "ui.ancillary_trust_database_admin.ConfirmInfoDialog",
        return_value=mock_confirm_dialog,
    )
    return mock_confirm_dialog


@pytest.fixture
def revert_dialog(revert_resp, mocker):
    # mock_revert_dialog = MagicMock(
    #     run=MagicMock(return_value=revert_resp), hide=MagicMock()
    # )
    # mocker.patch(
    #     "ui.ancillary_trust_database_admin.DeployConfirmDialog.get_ref",
    #     return_value=mock_revert_dialog,
    # )
    # return mock_revert_dialog
    return None


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
    mocker.patch(
        "ui.ancillary_trust_database_admin.fs.stat", return_value="stat for foo file"
    )
    trust = MagicMock(status="T", path="/tmp/foo", size=1, hash="abc")
    widget.on_file_selection_change(trust)
    widget.trustFileDetails.set_in_databae_view.assert_called_with(
        "File: /tmp/foo\nSize: 1\nSHA256: abc"
    )
    widget.trustFileDetails.set_on_file_system_view.assert_called_with(
        "stat for foo file\nSHA256: abc"
    )
    widget.trustFileDetails.set_trust_status.assert_called_with("This file is trusted.")


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
def test_on_confirm_deployment(widget, confirm_dialog, revert_dialog):
    parent = Gtk.Window()
    parent.add(widget.get_content())
    with patch("fapolicy_analyzer.System") as mock:
        instance = mock.return_value
        widget.system = instance
        widget.on_deployBtn_clicked()

        confirm_dialog.run.assert_called()
        confirm_dialog.hide.assert_called()
        instance.deploy.assert_called()


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.NO])
def test_on_neg_confirm_deployment(widget, confirm_dialog):
    parent = Gtk.Window()
    parent.add(widget.get_content())
    with patch("fapolicy_analyzer.System") as mock:
        instance = mock.return_value
        widget.system = instance
        widget.on_deployBtn_clicked()

        confirm_dialog.run.assert_called()
        confirm_dialog.hide.assert_called()
        instance.deploy.assert_not_called()


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
def test_on_revert_deployment(widget, confirm_dialog, revert_dialog, state):
    parent = Gtk.Window()
    parent.add(widget.get_content())

    with patch("fapolicy_analyzer.System") as mock:
        widget.system = mock.return_value
        mockChangeset = MagicMock()
        state.add_changeset_q(mockChangeset)
        assert len(state.get_changeset_q()) == 1
        widget.on_deployBtn_clicked()
        assert len(state.get_changeset_q()) == 0  # 1
        # revert_dialog.run.assert_called()
        # revert_dialog.hide.assert_called()


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.YES])
def test_on_neg_revert_deployment(widget, confirm_dialog, revert_dialog, state):
    parent = Gtk.Window()
    parent.add(widget.get_content())

    with patch("fapolicy_analyzer.System") as mock:
        widget.system = mock.return_value
        mockChangeset = MagicMock()
        state.add_changeset_q(mockChangeset)
        assert len(state.get_changeset_q()) == 1
        widget.on_deployBtn_clicked()
        assert len(state.get_changeset_q()) == 0
        # revert_dialog.run.assert_called()
        # revert_dialog.hide.assert_called()


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
