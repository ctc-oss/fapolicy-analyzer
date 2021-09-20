import context  # noqa: F401
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from helpers import delayed_gui_action
from ui.confirm_info_dialog import ConfirmInfoDialog
from ui.strings import CHANGESET_ACTION_ADD, CHANGESET_ACTION_DEL


def test_creates_widget():
    widget = ConfirmInfoDialog(parent=Gtk.Window())
    assert type(widget) is ConfirmInfoDialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = ConfirmInfoDialog(parent=parent)
    assert widget.get_transient_for() == parent


def test_dialog_actions_responses(mocker):
    mocker.patch(
        "ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    dialog = ConfirmInfoDialog(parent=Gtk.Window())
    for expected in [Gtk.ResponseType.YES, Gtk.ResponseType.NO]:
        button = dialog.get_widget_for_response(expected)
        delayed_gui_action(button.clicked, delay=1)
        response = dialog.run()
        assert response == expected


def test_load_path_action_list():
    path_action_list = [("/tmp/fu.txt", "Add"), ("/tmp/bar.txt", "Del")]
    widget = ConfirmInfoDialog(Gtk.Window(), path_action_list)

    scrollWindow = next(
        iter(
            filter(
                lambda x: isinstance(x, Gtk.ScrolledWindow),
                widget.get_content_area().get_children(),
            )
        )
    )
    view = scrollWindow.get_children()[0]
    rows = [x for x in view.get_model()]
    assert (CHANGESET_ACTION_ADD, path_action_list[0][0]) == (rows[0][0], rows[0][1])
    assert (CHANGESET_ACTION_DEL, path_action_list[1][0]) == (rows[1][0], rows[1][1])
