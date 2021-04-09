import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from helpers import delayed_gui_action
from ui.ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin


@pytest.fixture
def widget():
    return AncillaryTrustDatabaseAdmin()


def test_creates_widget(widget):
    assert type(widget.get_content()) is Gtk.Box


def test_status_markup(widget):
    assert widget._AncillaryTrustDatabaseAdmin__status_markup("T") == (
        "<b><u>T</u></b>/U",
        "light green",
    )
    assert widget._AncillaryTrustDatabaseAdmin__status_markup("U") == (
        "T/<b><u>U</u></b>",
        "gold",
    )
    assert widget._AncillaryTrustDatabaseAdmin__status_markup("foo") == (
        "T/U",
        "#FF3333",
    )


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
