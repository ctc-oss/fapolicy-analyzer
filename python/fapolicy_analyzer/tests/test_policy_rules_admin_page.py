import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.policy_rules_admin_page import PolicyRulesAdminPage


@pytest.fixture
def widget():
    return PolicyRulesAdminPage()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_adds_user_tabs(widget):
    tabs = widget.get_object("userTabs")
    page = tabs.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "User"
    page = tabs.get_nth_page(1)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "Group"
    page = tabs.get_nth_page(2)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "All"


def test_adds_subject_tabs(widget):
    tabs = widget.get_object("subjectTabs")
    page = tabs.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "Subject"


def test_adds_object_tabs(widget):
    tabs = widget.get_object("objectTabs")
    page = tabs.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "Object"


def test_updates_user_details(widget, mocker):
    mocker.patch("ui.policy_rules_admin_page.acl.getUserDetails", return_value="foo")
    textBuffer = widget.get_object("userDetails").get_buffer()
    widget.on_user_selection_changed(["fooUser", 1])
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_updates_group_details(widget, mocker):
    mocker.patch("ui.policy_rules_admin_page.acl.getGroupDetails", return_value="foo")
    textBuffer = widget.get_object("userDetails").get_buffer()
    widget.on_group_selection_changed(["fooGroup", 1])
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_updates_subject_details(widget, mocker):
    mocker.patch("ui.policy_rules_admin_page.fs.stat", return_value="foo")
    textBuffer = widget.get_object("subjectDetails").get_buffer()
    widget.on_subject_selection_changed(MagicMock(file=""))
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_updates_object_details(widget, mocker):
    mocker.patch("ui.policy_rules_admin_page.fs.stat", return_value="foo")
    textBuffer = widget.get_object("objectDetails").get_buffer()
    widget.on_object_selection_changed(MagicMock(file=""))
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )
