import context  # noqa: F401
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from helpers import delayed_gui_action
from ui.confirmation_dialog import ConfirmDialog


def test_creates_widget():
    widget = ConfirmDialog("foo")
    assert type(widget.get_content()) is Gtk.MessageDialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = ConfirmDialog("foo", parent=parent)
    assert widget.get_content().get_transient_for() == parent


def test_trust_database_admin_selection():
    dialog = ConfirmDialog("foo").get_content()
    for expected in [Gtk.ResponseType.YES, Gtk.ResponseType.NO]:
        button = dialog.get_widget_for_response(expected)
        delayed_gui_action(button.clicked)
        response = dialog.run()
        assert response == expected
