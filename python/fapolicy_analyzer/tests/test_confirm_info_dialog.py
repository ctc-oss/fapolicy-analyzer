import context  # noqa: F401
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from helpers import delayed_gui_action
from ui.confirm_info_dialog import ConfirmInfoDialog


def test_creates_widget():
    widget = ConfirmInfoDialog()
    assert type(widget) is ConfirmInfoDialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = ConfirmInfoDialog(parent=parent)
    assert widget.get_transient_for() == parent


def test_dialog_actions_responses():
    dialog = ConfirmInfoDialog()
    for expected in [Gtk.ResponseType.YES, Gtk.ResponseType.NO]:
        button = dialog.get_widget_for_response(expected)
        delayed_gui_action(button.clicked, delay=5)
        response = dialog.run()
        assert response == expected


def test_load_path_action_list():
    parent = Gtk.Window()
    widget = ConfirmInfoDialog(parent=parent)

    path_action_list = [("/tmp/fu.txt", "Add"), ("/tmp/bar.txt", "Del")]
    widget.load_path_action_list(path_action_list)

    # Verify the contents of the ConfirmInfoDialog.ListStore
    for i, j in zip(widget.changeStore, range(2)):
        # Note: tuples are reversed when loading Gtk.ListStore for display
        assert((i[1], i[0]) == path_action_list[j])
