import context  # noqa: F401
import pytest
import tempfile
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock, patch
from fapolicy_analyzer import Trust
from ui.ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from ui.strings import TRUSTED_FILE_MESSAGE, UNKNOWN_FILE_MESSAGE
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
    mock_revert_dialog = MagicMock(
        run=MagicMock(return_value=revert_resp), hide=MagicMock()
    )
    mocker.patch(
        "ui.ancillary_trust_database_admin.DeployConfirmDialog.get_ref",
        return_value=mock_revert_dialog,
    )
    return mock_revert_dialog


@pytest.fixture
def state():
    stateManager.del_changeset_q()
    yield stateManager
    stateManager.del_changeset_q()


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
    widget.trustFileDetails.set_trust_status.assert_called_with(TRUSTED_FILE_MESSAGE)


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
    widget.trustFileDetails.set_trust_status.assert_called_with(UNKNOWN_FILE_MESSAGE)


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
def test_on_confirm_deployment(widget, confirm_dialog, revert_dialog):
    parent = Gtk.Window()
    parent.add(widget.get_ref())
    with patch("fapolicy_analyzer.System") as mock:
        instance = mock.return_value
        widget.system = instance
        widget.on_deployBtn_clicked()

        confirm_dialog.run.assert_called()
        confirm_dialog.hide.assert_called()
        instance.deploy.assert_called()


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
def test_on_confirm_deployment_w_exception(
    widget, mocker, confirm_dialog, revert_dialog
):
    parent = Gtk.Window()
    parent.add(widget.get_ref())
    with patch("fapolicy_analyzer.System") as mock:
        mock.deploy = MagicMock(return_value=None, side_effect=BaseException)
        widget.system = mock
        widget.on_deployBtn_clicked()
        mock.deploy.assert_called()


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.NO])
def test_on_neg_confirm_deployment(widget, confirm_dialog):
    parent = Gtk.Window()
    parent.add(widget.get_ref())
    with patch("fapolicy_analyzer.System") as mock:
        widget.system = mock
        widget.on_deployBtn_clicked()

        confirm_dialog.run.assert_called()
        confirm_dialog.hide.assert_called()
        mock.deploy.assert_not_called()


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
def test_on_revert_deployment(widget, confirm_dialog, revert_dialog, state):
    parent = Gtk.Window()
    parent.add(widget.get_ref())

    with patch("fapolicy_analyzer.System") as mock:
        widget.system = mock.return_value
        mockChangeset = MagicMock()
        state.add_changeset_q(mockChangeset)
        assert len(state.get_changeset_q()) == 1
        widget.on_deployBtn_clicked()
        assert len(state.get_changeset_q()) == 1
        revert_dialog.run.assert_called()
        revert_dialog.hide.assert_called()


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.YES])
def test_on_neg_revert_deployment(widget, confirm_dialog, revert_dialog, state):
    parent = Gtk.Window()
    parent.add(widget.get_ref())

    with patch("fapolicy_analyzer.System") as mock:
        widget.system = mock.return_value
        mockChangeset = MagicMock()
        state.add_changeset_q(mockChangeset)
        assert len(state.get_changeset_q()) == 1
        widget.on_deployBtn_clicked()
        assert len(state.get_changeset_q()) == 0
        revert_dialog.run.assert_called()
        revert_dialog.hide.assert_called()


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
    widget.on_trust_selection_changed(trust)
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
    widget.on_trust_selection_changed(trust)
    widget.on_untrustBtn_clicked()
    assert len(state.get_changeset_q()) == 1


def test_on_untrustBtn_clicked_empty(widget, state):
    assert len(state.get_changeset_q()) == 0
    widget.on_untrustBtn_clicked()
    assert len(state.get_changeset_q()) == 0


def test_on_file_added(widget, state):
    assert len(state.get_changeset_q()) == 0
    tmpFile = tempfile.NamedTemporaryFile()
    widget.on_files_added([tmpFile.name])
    assert len(state.get_changeset_q()) == 1


def test_on_file_added_empty(widget, state):
    assert len(state.get_changeset_q()) == 0
    widget.on_files_added(None)
    assert len(state.get_changeset_q()) == 0


def test_on_file_deleted(widget, state):
    assert len(state.get_changeset_q()) == 0
    tmpFile = tempfile.NamedTemporaryFile()
    widget.on_files_deleted([tmpFile.name])
    assert len(state.get_changeset_q()) == 1


def test_on_file_deleted_empty(widget, state):
    assert len(state.get_changeset_q()) == 0
    widget.on_files_deleted(None)
    assert len(state.get_changeset_q()) == 0


# ########################## Edit Session Related ####################
def test_on_session_load(widget, mocker):
    # Submit to flake8/linting - Line was too long
    strModule = "ui.ancillary_trust_database_admin.AncillaryTrustDatabaseAdmin"
    mockAdd = mocker.patch("{}.on_files_added".format(strModule))
    mockDel = mocker.patch("{}.on_files_deleted".format(strModule))

    listPaTuples = [
        ("/data_space/man_from_mars.txt", "Add"),
        ("/data_space/this/is/a/longer/path/now_is_the_time.txt", "Del"),
        ("/data_space/Integration.json", "Add"),
    ]
    listPaAddedExpected = [
        "/data_space/man_from_mars.txt",
        "/data_space/Integration.json",
    ]
    listPaDeletedExpected = ["/data_space/this/is/a/longer/path/now_is_the_time.txt"]

    widget.on_session_load(listPaTuples)
    mockAdd.assert_called_with(listPaAddedExpected)
    mockDel.assert_called_with(listPaDeletedExpected)


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
def test_handle_deploy_excption(widget, confirm_dialog):
    parent = Gtk.Window()
    parent.add(widget.get_ref())

    with patch("fapolicy_analyzer.System") as mock:
        mock.deploy = MagicMock(
            return_value=None, side_effect=Exception("mocked error")
        )
        widget.system = mock
        with pytest.raises(Exception) as excinfo:
            widget.on_deployBtn_clicked()
            assert excinfo.value.message == "mocked error"
