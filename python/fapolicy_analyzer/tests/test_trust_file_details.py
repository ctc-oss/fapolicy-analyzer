import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui.trust_file_details import TrustFileDetails


@pytest.fixture
def widget():
    return TrustFileDetails()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_sets_In_Database_View(widget):
    textView = widget.get_object("inDatabaseView")
    textBuffer = textView.get_buffer()
    widget.set_in_database_view("foo")
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_sets_On_File_System_View(widget):
    textView = widget.get_object("onFileSystemView")
    textBuffer = textView.get_buffer()
    widget.set_on_file_system_view("foo")
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_sets_trust_status(widget):
    textView = widget.get_object("fileTrustStatusView")
    textBuffer = textView.get_buffer()
    widget.set_trust_status("foo")
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_clear(widget):
    widget.set_in_database_view("foo")
    widget.set_on_file_system_view("foo")
    widget.set_trust_status("foo")
    widget.clear()
    buffers = [
        widget.get_object("inDatabaseView").get_buffer(),
        widget.get_object("onFileSystemView").get_buffer(),
        widget.get_object("fileTrustStatusView").get_buffer(),
    ]
    assert not any(
        [b.get_text(b.get_start_iter(), b.get_end_iter(), True) for b in buffers]
    )
