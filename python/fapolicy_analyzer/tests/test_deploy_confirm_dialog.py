import context  # noqa: F401
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui.deploy_confirm_dialog import DeployConfirmDialog


def test_creates_widget():
    widget = DeployConfirmDialog()
    assert type(widget.get_content()) is Gtk.MessageDialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = DeployConfirmDialog(parent)
    assert widget.get_content().get_transient_for() == parent


def test_closes_after_cancel_time():
    widget = DeployConfirmDialog(cancel_time=1)
    result = widget.get_content().run()
    assert result == Gtk.ResponseType.NO
