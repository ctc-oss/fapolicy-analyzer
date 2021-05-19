import context  # noqa: F401
import pytest
import locale
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.main_window import MainWindow
from ui.analyzer_selection_dialog import ANALYZER_SELECTION


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
def es_locale():
    locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
    yield
    locale.setlocale(locale.LC_ALL, "")


def test_displays_window(mainWindow):
    assert type(mainWindow.window) is Gtk.Window
    assert mainWindow.window.get_title() == "File Access Policy Analyzer"


def test_displays_about_dialog(mainWindow, mocker):
    aboutDialog = mainWindow.builder.get_object("aboutDialog")
    menuItem = mainWindow.builder.get_object("aboutMenu")
    mocker.patch.object(aboutDialog, "run", return_value=0)
    menuItem.activate()
    aboutDialog.run.assert_called()


def test_opens_trust_db_admin_page(mocker):
    mockDialog = MagicMock()
    mockDialog.run.return_value = ANALYZER_SELECTION.TRUST_DATABASE_ADMIN.value
    mockComponent = MagicMock()
    mockComponent.get_content.return_value = mockDialog
    mocker.patch(
        "ui.main_window.AnalyzerSelectionDialog",
        return_value=mockComponent,
    )
    mainWindow = MainWindow()
    content = next(iter(mainWindow.builder.get_object("mainContent").get_children()))
    assert (
        content.get_tab_label_text(content.get_nth_page(0)) == "System Trust Database"
    )


def test_raises_bad_selection_error(mainWindow, mocker):
    mockDialog = MagicMock()
    mockDialog.run.return_value = -1
    mockComponent = MagicMock()
    mockComponent.get_content.return_value = mockDialog
    mocker.patch(
        "ui.main_window.AnalyzerSelectionDialog",
        return_value=mockComponent,
    )
    with pytest.raises(Exception, match="Bad Selection"):
        mainWindow.original_on_start()


def test_localization(es_locale):
    mainWindow = StubMainWindow()
    assert type(mainWindow.window) is Gtk.Window
    assert (
        mainWindow.window.get_title() == "Analizador de políticas de acceso a archivos"
    )
