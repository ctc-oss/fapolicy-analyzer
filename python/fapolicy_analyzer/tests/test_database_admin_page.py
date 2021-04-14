import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from mocks import mock_System
from helpers import refresh_gui
from ui.database_admin_page import DatabaseAdminPage


@pytest.fixture
def widget(mocker):
    mocker.patch("ui.database_admin_page.System", return_value=mock_System())
    widget = DatabaseAdminPage()
    refresh_gui()
    return widget


def test_creates_widget(widget):
    assert type(widget.get_content()) is Gtk.Notebook


def test_appends_system_db_admin_tab(widget):
    content = widget.get_content()
    page = content.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert content.get_tab_label_text(page) == "System Trust Database"


def test_appends_ancillary_db_admin_tab(widget):
    content = widget.get_content()
    page = content.get_nth_page(1)
    assert type(page) is Gtk.Box
    assert content.get_tab_label_text(page) == "Ancillary Trust Database"
