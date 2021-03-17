import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui.main_window import MainWindow


class StubMainWindow(MainWindow):
    """
    Need to stub the MainWindow class to prevent the AnalyzerSelectionDialog from opening
    on start and hanging the tests
    """

    __module__ = "ui.main_window"

    def on_start(self, *args):
        pass


@pytest.fixture
def mainWindow():
    mainWindow = StubMainWindow()
    yield mainWindow
    mainWindow.window.destroy()


def test_displays_window(mainWindow):
    assert type(mainWindow.window) is Gtk.Window
    assert mainWindow.window.get_title() == "File Access Policy Analyzer"
