import context  # noqa: F401
import pytest
import locale
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from fapolicy_analyzer import Changeset
from helpers import refresh_gui
from ui.main_window import MainWindow, router
from ui.state_manager import stateManager, NotificationType
from ui.strings import AUTOSAVE_RESTORE_ERROR_MSG


@pytest.fixture
def mainWindow():
    return MainWindow()


@pytest.fixture
def state():
    yield stateManager
    stateManager.del_changeset_q()
    stateManager.systemNotification = None


@pytest.fixture
def es_locale():
    locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
    yield
    locale.setlocale(locale.LC_ALL, "")


def test_displays_window(mainWindow):
    window = mainWindow.get_ref()
    assert type(window) is Gtk.Window
    assert window.get_title() == "File Access Policy Analyzer"


def test_shows_confirm_if_unapplied_changes(mainWindow, state, mocker):
    # Populate a Changeset, add it to the StateManager's queue
    cs = Changeset()
    strFilename = "/tmp/DeadBeef.txt"
    cs.add_trust(strFilename)
    stateManager.add_changeset_q(cs)
    mockDialog = MagicMock()
    mockDialog.run.return_value = False
    mocker.patch(
        "ui.main_window.UnappliedChangesDialog.get_ref",
        return_value=mockDialog,
    )
    mainWindow.get_object("quitMenu").activate()
    mockDialog.run.assert_called()


def test_does_not_show_confirm_if_no_unapplied_changes(mainWindow, state, mocker):
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


def test_opens_trust_db_admin_page(mainWindow, mocker):
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

    mockTFunc = mocker.patch(
        "ui.trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mockATFunc = mocker.patch(
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
    mockTFunc.assert_called()
    mockATFunc.assert_called()
    assert Gtk.Buildable.get_name(content) == "policyRulesAdminPage"


def test_bad_router_option():
    with pytest.raises(Exception) as excinfo:
        router("foo")
        assert excinfo.value.message == "Bad Selection"


def test_localization(es_locale):
    mainWindow = MainWindow()
    window = mainWindow.get_ref()
    assert type(window) is Gtk.Window
    assert window.get_title() == "Analizador de políticas de acceso a archivos"


def test_on_delete_event(mainWindow):
    window = mainWindow
    bReturn = window.on_delete_event(None)
    assert not bReturn


def test_on_openMenu_activate(mainWindow, state, mocker):
    # Mock the FileChooser dlg
    mockDialog = MagicMock()
    mockDialog.run.return_value = Gtk.ResponseType.OK
    mockDialog.get_filename.return_value = "/tmp/open_tmp.json"
    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog",
        return_value=mockDialog,
    )

    mocker.patch("ui.main_window.stateManager.open_edit_session", return_value=True)

    mocker.patch("ui.main_window.path.isfile", return_value=True)
    mainWindow.get_object("openMenu").activate()
    stateManager.open_edit_session.assert_called_with("/tmp/open_tmp.json")


def test_on_openMenu_activate_fail(mainWindow, state, mocker):
    fakeFile = "/tmp/open_tmp.json"
    mockDialog = MagicMock()
    mockDialog.run.return_value = Gtk.ResponseType.OK
    mockDialog.get_filename.return_value = fakeFile
    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog",
        return_value=mockDialog,
    )

    mocker.patch("ui.main_window.stateManager.open_edit_session", return_value=False)

    mocker.patch("ui.main_window.path.isfile", return_value=True)
    mockHandler = MagicMock()
    state.system_notification_added += mockHandler
    mainWindow.get_object("openMenu").activate()
    mockHandler.assert_called_with(
        (
            f"An error occurred trying to open the session file, {fakeFile}",
            NotificationType.ERROR,
        )
    )
    state.system_notification_added -= mockHandler


def test_on_restoreMenu_activate(mainWindow, state, mocker):
    # Invoke 'pass'ed function
    mainWindow.get_object("restoreMenu").activate()


def test_on_restoreMenu_activate_w_exception(mainWindow, state, mocker):
    """
    Test the callback bound to the File|Restore menu-item. The
    StateManager::restore_previous_session() is mocked to fail with an
    exception thrown.
    """
    mockRestoreAutosave = mocker.patch(
        "ui.state_manager.StateManager.restore_previous_session", side_effect=IOError
    )

    mainWindow.get_object("restoreMenu").activate()
    mockRestoreAutosave.assert_called()


def test_on_saveAsMenu_activate(mainWindow, state, mocker):
    # Mock the FileChooser dlg
    mockDialog = MagicMock()
    mockDialog.run.return_value = Gtk.ResponseType.OK
    mockDialog.get_filename.return_value = "/tmp/save_as_tmp.json"
    mocker.patch(
        "ui.main_window.Gtk.FileChooserDialog",
        return_value=mockDialog,
    )

    # Mock the StateMgr interface
    mockFunc = mocker.patch(
        "ui.main_window.stateManager.save_edit_session", return_value=True
    )

    mainWindow.get_object("saveAsMenu").activate()
    mockFunc.assert_called_with("/tmp/save_as_tmp.json")


def test_on_saveMenu_activate(mainWindow, state, mocker):
    # Mock the on_saveAsMenu_activate() call
    mockFunc = mocker.patch(
        "ui.main_window.MainWindow.on_saveAsMenu_activate", return_value=True
    )

    # Mock the StateMgr interface
    mocker.patch("ui.main_window.stateManager.save_edit_session", return_value=True)

    window = mainWindow
    window.get_object("saveMenu").activate()
    mockFunc.assert_called()


def test_on_saveMenu_activate_w_set_filename(mainWindow, state, mocker):
    mainWindow.strSessionFilename = "/tmp/save_w_filename_tmp.json"

    # Mock the StateMgr interface
    mocker.patch("ui.main_window.stateManager.save_edit_session", return_value=True)

    mainWindow.get_object("saveMenu").activate()
    stateManager.save_edit_session.assert_called_with("/tmp/save_w_filename_tmp.json")


def test_on_start(mainWindow, mocker):
    mockDetectAutosave = mocker.patch(
        "ui.state_manager.StateManager.detect_previous_session", return_value=False
    )
    MainWindow()
    mockDetectAutosave.assert_called()


def test_on_start_w_declined_restore(mocker):
    """
    Test specifically for exercising the on_start() functionality.
    Mocks:
    1. The StateManager::detect_previous_session() returning True simulating
    the detection of an autosaved session file.
    2. The StateManager::restore_previous_session() to simulate successfully
    loading the autosaved session file.
    3. The Gtk.Dialog which will return Gtk.ResponseType.NO to circumvent
    the blocking that would occur waiting for a user's response.
    """

    mockDetectAutosave = mocker.patch(
        "ui.state_manager.StateManager.detect_previous_session", return_value=True
    )

    mockGtkDialog = mocker.patch(
        "gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.NO
    )

    MainWindow()
    mockDetectAutosave.assert_called()
    mockGtkDialog.assert_called()


def test_on_start_w_accepted_restore(mocker):
    """
    Test specifically for exercising the on_start() functionality.
    Mocks:
    1. The StateManager::detect_previous_session() returning True simulating
    the detection of an autosaved session file.
    2. The StateManager::restore_previous_session() to simulate successfully
    loading the autosaved session file.
    3. The Gtk.Dialog which will return Gtk.ResponseType.NO to circumvent
    the blocking that would occur waiting for a user's response.
    """

    mockDetectAutosave = mocker.patch(
        "ui.state_manager.StateManager.detect_previous_session", return_value=True
    )

    mockRestoreAutosave = mocker.patch(
        "ui.state_manager.StateManager.restore_previous_session", return_value=True
    )

    mockGtkDialog = mocker.patch(
        "gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.YES
    )

    MainWindow()
    mockDetectAutosave.assert_called()
    mockGtkDialog.assert_called()
    mockRestoreAutosave.assert_called()


def test_on_start_w_restore_exception(mocker):
    """
    Test specifically for exercising the on_start() functionality.
    Mocks:
    1. The StateManager::detect_previous_session() returning True simulating
    the detection of an autosaved session file.
    2. The StateManager::restore_previous_session() to simulate successfully
    loading the autosaved session file.
    3. The Gtk.Dialog which will return Gtk.ResponseType.NO to circumvent
    the blocking that would occur waiting for a user's response.
    """

    mockDetectAutosave = mocker.patch(
        "ui.state_manager.StateManager.detect_previous_session", return_value=True
    )

    mockRestoreAutosave = mocker.patch(
        "ui.state_manager.StateManager.restore_previous_session", side_effect=IOError
    )

    mockGtkDialog = mocker.patch(
        "gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.YES
    )

    MainWindow()
    mockDetectAutosave.assert_called()
    mockGtkDialog.assert_called()
    mockRestoreAutosave.assert_called()


def test_on_start_w_failed_restore(state, mocker):
    mocker.patch(
        "ui.state_manager.StateManager.detect_previous_session", return_value=True
    )
    mocker.patch(
        "ui.state_manager.StateManager.restore_previous_session", return_value=False
    )
    mocker.patch("gi.repository.Gtk.Dialog.run", return_value=Gtk.ResponseType.YES)

    mockHandler = MagicMock()
    state.system_notification_added += mockHandler
    MainWindow()
    mockHandler.assert_called_with((AUTOSAVE_RESTORE_ERROR_MSG, NotificationType.ERROR))
    state.system_notification_added -= mockHandler
