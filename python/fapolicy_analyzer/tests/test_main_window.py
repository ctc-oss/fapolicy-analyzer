import context  # noqa: F401
import pytest
import locale
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.main_window import MainWindow
from ui.analyzer_selection_dialog import ANALYZER_SELECTION
from ui.state_manager import stateManager


class StubMainWindow(MainWindow):
    """
    Need to stub the MainWindow class to prevent the AnalyzerSelectionDialog from opening
    on start and hanging the tests
    """

    __module__ = "ui.main_window"

    def on_start(self, *args):
        pass

    def original_on_start(self, *args):
        super().on_start(*args)


@pytest.fixture
def mainWindow():
    return StubMainWindow()


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
    stateManager.add_changeset_q("foo")
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


def test_opens_trust_db_admin_page(mocker):
    mockDialog = MagicMock()
    mockDialog.get_selection.return_value = ANALYZER_SELECTION.TRUST_DATABASE_ADMIN
    mocker.patch(
        "ui.main_window.AnalyzerSelectionDialog",
        return_value=mockDialog,
    )
    mainWindow = MainWindow()
    content = next(iter(mainWindow.get_object("mainContent").get_children()))
    assert (
        content.get_tab_label_text(content.get_nth_page(0)) == "System Trust Database"
    )


def test_raises_bad_selection_error(mainWindow, mocker):
    mockDialog = MagicMock()
    mockDialog.run.return_value = -1
    mockComponent = MagicMock()
    mockComponent.get_ref.return_value = mockDialog
    mocker.patch(
        "ui.main_window.AnalyzerSelectionDialog",
        return_value=mockComponent,
    )
    with pytest.raises(Exception, match="Bad Selection"):
        mainWindow.original_on_start()


def test_localization(es_locale):
    mainWindow = StubMainWindow()
    window = mainWindow.get_ref()
    assert type(window) is Gtk.Window
    assert window.get_title() == "Analizador de políticas de acceso a archivos"

def test_on_delete_event(mainWindow):
    window = mainWindow
    bReturn = window.on_delete_event(None)
    assert not bReturn

def test_on_openMenu_activate(mainWindow):
    window = mainWindow
    window.on_openMenu_activate(None)

def test_on_restoreMenu_activate(mainWindow):
    window = mainWindow
    window.on_restoreMenu_activate(None)

def test_on_saveMenu_activate(mainWindow):
    window = mainWindow
    window.on_saveMenu_activate(None)

def test_on_saveAsMenu_activate(mainWindow):
    window = mainWindow
    window.on_saveAsMenu_activate(None)
