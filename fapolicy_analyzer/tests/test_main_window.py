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

import locale

import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock

from callee import Attrs, InstanceOf
from fapolicy_analyzer import Changeset
from gi.repository import Gtk
from redux import Action
from rx import create
from rx.subject import Subject
from ui.actions import ADD_NOTIFICATION
from ui.main_window import MainWindow, ServiceStatus, router
from ui.session_manager import NotificationType, sessionManager
from ui.store import init_store
from ui.strings import AUTOSAVE_RESTORE_ERROR_MSG

from helpers import refresh_gui
from mocks import mock_System

test_changeset = Changeset()
test_changeset.add_trust("/tmp/DeadBeef.txt")


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("ui.main_window.dispatch")


@pytest.fixture
def mock_init_store():
    init_store(mock_System())


@pytest.fixture
def mock_system_features(changesets, mocker):
    def push_changeset(observer, *args):
        observer.on_next({"changesets": changesets})
        observer.on_completed()

    system_features_mock = create(push_changeset)
    mocker.patch("ui.main_window.get_system_feature", return_value=system_features_mock)


@pytest.fixture
def mock_dispatches(mocker):
    mocker.patch("ui.ancillary_trust_database_admin.dispatch")
    mocker.patch("ui.system_trust_database_admin.dispatch")
    mocker.patch("ui.policy_rules_admin_page.dispatch")


@pytest.fixture
@pytest.mark.usefixtures("mock_system_features")
def mainWindow(mock_init_store, mock_dispatches):
    return MainWindow()


@pytest.fixture
def es_locale():
    locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
    yield
    locale.setlocale(locale.LC_ALL, "")


def test_displays_window(mainWindow):
    window = mainWindow.get_ref()
    assert type(window) is Gtk.Window
    assert window.get_title() == "File Access Policy Analyzer"


@pytest.mark.usefixtures("mock_system_features")
@pytest.mark.parametrize("changesets", [[test_changeset]])
def test_shows_confirm_if_unapplied_changes(mainWindow, mocker):
    mockDialog = MagicMock()
    mockDialog.run.return_value = False
    mocker.patch(
        "ui.main_window.UnappliedChangesDialog.get_ref",
        return_value=mockDialog,
    )
    mainWindow.get_object("quitMenu").activate()
    mockDialog.run.assert_called()


def test_does_not_show_confirm_if_no_unapplied_changes(mainWindow, mocker):
    mockDialog = MagicMock()
    mockDialog.run.return_value = False
    mocker.patch(
        "ui.main_window.UnappliedChangesDialog.get_ref",
        return_value=mockDialog,
    )
    mainWindow.get_object("quitMenu").activate()
    mockDialog.run.assert_not_called()


def test_displays_about_dialog(mainWindow, mocker):
    aboutDialog = mainWindow.get_object("aboutDialog")
    menuItem = mainWindow.get_object("aboutMenu")
    mocker.patch.object(aboutDialog, "run", return_value=0)
    menuItem.activate()
    aboutDialog.run.assert_called()


def test_defaults_to_trust_db_admin_page(mainWindow):
    content = next(iter(mainWindow.get_object("mainContent").get_children()))
    assert (
        content.get_tab_label_text(content.get_nth_page(0)) == "System Trust Database"
    )


def test_opens_trust_db_admin_page(mainWindow):
    mainContent = mainWindow.get_object("mainContent")
    mainContent.remove(next(iter(mainContent.get_children())))
    assert not mainContent.get_children()
    menuItem = mainWindow.get_object("trustDbMenu")
    menuItem.activate()
    content = next(iter(mainContent.get_children()))
    assert (
        content.get_tab_label_text(content.get_nth_page(0)) == "System Trust Database"
    )


def test_opens_analyze_with_audit_page(mainWindow, mocker):
    menuItem = mainWindow.get_object("analyzeMenu")

    mocker.patch(
        "ui.trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch(
        "ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog.get_filename",
        return_value="foo",
    )
    mocker.patch("ui.main_window.path.isfile", return_value=True)
    menuItem.activate()
    refresh_gui()
    content = next(iter(mainWindow.get_object("mainContent").get_children()))
    assert Gtk.Buildable.get_name(content) == "policyRulesAdminPage"


def test_opens_analyze_with_syslog_page(mainWindow, mocker):
    menuItem = mainWindow.get_object("syslogMenu")
    menuItem.activate()
    refresh_gui()
    content = next(iter(mainWindow.get_object("mainContent").get_children()))
    assert Gtk.Buildable.get_name(content) == "policyRulesAdminPage"


def test_bad_router_option():
    with pytest.raises(Exception) as excinfo:
        router("foo")
        assert excinfo.value.message == "Bad Selection"


@pytest.mark.usefixtures("es_locale", "mock_init_store", "mock_dispatches")
def test_localization():
    mainWindow = MainWindow()
    window = mainWindow.get_ref()
    assert type(window) is Gtk.Window
    assert window.get_title() == "Analizador de políticas de acceso a archivos"


def test_on_delete_event(mainWindow):
    window = mainWindow
    bReturn = window.on_delete_event(None)
    assert not bReturn


def test_on_openMenu_activate(mainWindow, mocker):
    # Mock the FileChooser dlg
    mockDialog = MagicMock()
    mockDialog.run.return_value = Gtk.ResponseType.OK
    mockDialog.get_filename.return_value = "/tmp/open_tmp.json"
    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog",
        return_value=mockDialog,
    )

    mocker.patch("ui.main_window.sessionManager.open_edit_session", return_value=True)

    mocker.patch("ui.main_window.path.isfile", return_value=True)
    mainWindow.get_object("openMenu").activate()
    sessionManager.open_edit_session.assert_called_with("/tmp/open_tmp.json")


def test_on_openMenu_activate_fail(mainWindow, mock_dispatch, mocker):
    fakeFile = "/tmp/open_tmp.json"
    mockDialog = MagicMock()
    mockDialog.run.return_value = Gtk.ResponseType.OK
    mockDialog.get_filename.return_value = fakeFile
    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog",
        return_value=mockDialog,
    )

    mocker.patch("ui.main_window.sessionManager.open_edit_session", return_value=False)

    mocker.patch("ui.main_window.path.isfile", return_value=True)
    mainWindow.get_object("openMenu").activate()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.ERROR,
                text=f"An error occurred trying to open the session file, {fakeFile}",
            ),
        )
    )


def test_on_restoreMenu_activate(mainWindow, mocker):
    mocker.patch("glob.glob", return_value=["foo"])
    mock = mocker.patch(
        "ui.main_window.sessionManager.open_edit_session", return_value=True
    )
    mainWindow.get_object("restoreMenu").activate()
    mock.assert_called_with("foo")


def test_on_restoreMenu_activate_w_exception(mainWindow, mocker):
    """
    Test the callback bound to the File|Restore menu-item. The
    sessionManager::restore_previous_session() is mocked to fail with an
    exception thrown.
    """
    mockRestoreAutosave = mocker.patch(
        "ui.main_window.sessionManager.restore_previous_session", side_effect=IOError
    )

    mainWindow.get_object("restoreMenu").activate()
    mockRestoreAutosave.assert_called()


def test_on_saveAsMenu_activate(mainWindow, mocker):
    # Mock the FileChooser dlg
    mockDialog = MagicMock()
    mockDialog.run.return_value = Gtk.ResponseType.OK
    mockDialog.get_filename.return_value = "/tmp/save_as_tmp.json"
    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog",
        return_value=mockDialog,
    )
    mockFunc = mocker.patch(
        "ui.main_window.sessionManager.save_edit_session", return_value=True
    )

    mainWindow.get_object("saveAsMenu").activate()
    mockFunc.assert_called_with([], "/tmp/save_as_tmp.json")


def test_on_saveMenu_activate(mainWindow, mocker):
    # Mock the on_saveAsMenu_activate() call
    mockFunc = mocker.patch(
        "ui.main_window.MainWindow.on_saveAsMenu_activate", return_value=True
    )
    mocker.patch("ui.main_window.sessionManager.save_edit_session", return_value=True)

    window = mainWindow
    window.get_object("saveMenu").activate()
    mockFunc.assert_called()


def test_on_saveMenu_activate_w_set_filename(mainWindow, mocker):
    mainWindow.strSessionFilename = "/tmp/save_w_filename_tmp.json"
    mocker.patch("ui.main_window.sessionManager.save_edit_session", return_value=True)

    mainWindow.get_object("saveMenu").activate()
    sessionManager.save_edit_session.assert_called_with(
        [], "/tmp/save_w_filename_tmp.json"
    )


@pytest.mark.usefixtures("mock_init_store", "mock_dispatches")
def test_on_start(mocker):
    mockDetectAutosave = mocker.patch(
        "ui.main_window.sessionManager.detect_previous_session", return_value=False
    )
    MainWindow()
    mockDetectAutosave.assert_called()


@pytest.mark.usefixtures("mock_init_store", "mock_dispatches")
def test_on_start_w_declined_restore(mocker):
    """
    Test specifically for exercising the on_start() functionality.
    Mocks:
    1. The sessionManager::detect_previous_session() returning True simulating
    the detection of an autosaved session file.
    2. The sessionManager::restore_previous_session() to simulate successfully
    loading the autosaved session file.
    3. The Gtk.Dialog which will return Gtk.ResponseType.NO to circumvent
    the blocking that would occur waiting for a user's response.
    """

    mockDetectAutosave = mocker.patch(
        "ui.main_window.sessionManager.detect_previous_session", return_value=True
    )

    mockGtkDialog = mocker.patch(
        "gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.NO
    )

    MainWindow()
    mockDetectAutosave.assert_called()
    mockGtkDialog.assert_called()


@pytest.mark.usefixtures("mock_init_store", "mock_dispatches")
def test_on_start_w_accepted_restore(mocker):
    """
    Test specifically for exercising the on_start() functionality.
    Mocks:
    1. The sessionManager::detect_previous_session() returning True simulating
    the detection of an autosaved session file.
    2. The sessionManager::restore_previous_session() to simulate successfully
    loading the autosaved session file.
    3. The Gtk.Dialog which will return Gtk.ResponseType.NO to circumvent
    the blocking that would occur waiting for a user's response.
    """

    mockDetectAutosave = mocker.patch(
        "ui.main_window.sessionManager.detect_previous_session", return_value=True
    )

    mockRestoreAutosave = mocker.patch(
        "ui.main_window.sessionManager.restore_previous_session", return_value=True
    )

    mockGtkDialog = mocker.patch(
        "gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.YES
    )

    MainWindow()
    mockDetectAutosave.assert_called()
    mockGtkDialog.assert_called()
    mockRestoreAutosave.assert_called()


@pytest.mark.usefixtures("mock_init_store", "mock_dispatches")
def test_on_start_w_restore_exception(mocker):
    """
    Test specifically for exercising the on_start() functionality.
    Mocks:
    1. The sessionManager::detect_previous_session() returning True simulating
    the detection of an autosaved session file.
    2. The sessionManager::restore_previous_session() to simulate successfully
    loading the autosaved session file.
    3. The Gtk.Dialog which will return Gtk.ResponseType.NO to circumvent
    the blocking that would occur waiting for a user's response.
    """

    mockDetectAutosave = mocker.patch(
        "ui.main_window.sessionManager.detect_previous_session", return_value=True
    )

    mockRestoreAutosave = mocker.patch(
        "ui.main_window.sessionManager.restore_previous_session", side_effect=IOError
    )

    mockGtkDialog = mocker.patch(
        "gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.YES
    )

    MainWindow()
    mockDetectAutosave.assert_called()
    mockGtkDialog.assert_called()
    mockRestoreAutosave.assert_called()


@pytest.mark.usefixtures("mock_init_store", "mock_dispatches")
def test_on_start_w_failed_restore(mock_dispatch, mocker):
    mocker.patch(
        "ui.main_window.sessionManager.detect_previous_session", return_value=True
    )
    mocker.patch(
        "ui.main_window.sessionManager.restore_previous_session", return_value=False
    )
    mocker.patch("gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.YES)

    MainWindow()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.ERROR,
                text=AUTOSAVE_RESTORE_ERROR_MSG,
            ),
        )
    )


def test_toolbar_deploy_operation(mainWindow, mocker):
    mocker.patch("ui.operations.deploy_changesets_op.get_system_feature")
    mockDeploy = mocker.patch("ui.main_window.DeployChangesetsOp.run")
    tool_bar = MainWindow().get_object("appArea").get_children()[1]
    deploy_btn = tool_bar.get_nth_item(0)
    deploy_btn.get_child().clicked()
    mockDeploy.assert_called_once()


def test_toggles_deploy_changes_toolbar_btn(mocker):
    system_features_mock = Subject()
    mocker.patch(
        "ui.main_window.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    tool_bar = MainWindow().get_object("appArea").get_children()[1]
    deploy_btn = tool_bar.get_nth_item(0)
    assert not deploy_btn.get_sensitive()
    system_features_mock.on_next({"changesets": ["foo"]})
    assert deploy_btn.get_sensitive()
    system_features_mock.on_next({"changesets": []})
    assert not deploy_btn.get_sensitive()


def test_toggles_dirty_title(mocker):
    system_features_mock = Subject()
    mocker.patch(
        "ui.main_window.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    windowRef = MainWindow().get_ref()
    assert not windowRef.get_title().startswith("*")
    system_features_mock.on_next({"changesets": ["foo"]})
    assert windowRef.get_title().startswith("*")
    system_features_mock.on_next({"changesets": []})
    assert not windowRef.get_title().startswith("*")


# Testing fapd daemon interfacing
def test_on_fapdStartMenu_activate(mainWindow, mocker):
    mockHandle = MagicMock()
    mainWindow._fapd_ref = mockHandle
    mainWindow._fapd_status = False
    mainWindow.get_object("fapdStartMenu").activate()
    mockHandle.start.assert_called()


def test_on_fapdStopMenu_activate(mainWindow, mocker):
    mockHandle = MagicMock()
    mainWindow._fapd_ref = mockHandle
    mainWindow._fapd_status = True
    mainWindow.get_object("fapdStopMenu").activate()
    mockHandle.stop.assert_called()


def test_on_update_daemon_status(mainWindow, mocker):
    mainWindow.on_update_daemon_status(True)
    assert mainWindow._fapd_status

    mainWindow.on_update_daemon_status(False)
    assert not mainWindow._fapd_status


def test_start_daemon_monitor(mainWindow, mocker):
    mockThread = MagicMock()
    mocker.patch(
        "ui.main_window.Thread",
        return_value=mockThread,
    )
    mainWindow._fapd_status = False
    mainWindow._start_daemon_monitor()
    mockThread.start.assert_called_once()


def test_update_fapd_status(mainWindow, mocker):
    mainWindow._update_fapd_status(ServiceStatus.TRUE)
    tupleIdSize = mainWindow.get_object("fapdStatusLight").get_icon_name()
    assert tupleIdSize == ("emblem-default", 4)
    mainWindow._update_fapd_status(ServiceStatus.FALSE)
    tupleIdSize = mainWindow.get_object("fapdStatusLight").get_icon_name()
    assert tupleIdSize == ("process-stop", 4)
    mainWindow._update_fapd_status(ServiceStatus.UNKNOWN)
    tupleIdSize = mainWindow.get_object("fapdStatusLight").get_icon_name()
    assert tupleIdSize == ("edit-delete", 4)
