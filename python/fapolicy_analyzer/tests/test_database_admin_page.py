import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.database_admin_page import DatabaseAdminPage


@pytest.fixture
def widget(mocker):
    mocker.patch(
        "ui.database_admin_page.AncillaryTrustDatabaseAdmin",
        return_value=MagicMock(get_content=MagicMock(return_value=Gtk.Box())),
    )
    mocker.patch(
        "ui.database_admin_page.SystemTrustDatabaseAdmin",
        return_value=MagicMock(get_content=MagicMock(return_value=Gtk.Box())),
    )
    return DatabaseAdminPage()


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
