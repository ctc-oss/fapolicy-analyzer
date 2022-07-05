# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re

import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock

from gi.repository import Gtk
from ui.configs import Colors
from ui.object_list import ObjectList
from ui.strings import FILE_LABEL, FILES_LABEL


def _mock_object(trust="", mode="", access="", file="", trust_status=""):
    return MagicMock(
        trust=trust, mode=mode, access=access, file=file, trust_status=trust_status
    )


_objects = [
    _mock_object(trust="ST", mode="R", access="A", file="/tmp/foo", trust_status="U"),
    _mock_object(trust="AT", mode="W", access="A", file="/tmp/baz", trust_status="U"),
    _mock_object(trust="U", mode="X", access="D", file="/tmp/bar", trust_status="U"),
]

_ids = [1, 2, 3]


@pytest.fixture
def widget():
    return ObjectList()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_store(widget):
    def strip_markup(markup):
        return re.search(r"<b>([A-Z]*)</b>", markup).group(1)

    widget.load_store(_objects, ids=_ids)
    view = widget.get_object("treeView")
    sortedObjects = sorted(_objects, key=lambda o: o.file)
    assert [t.trust for t in sortedObjects] == [
        strip_markup(x[0]) for x in view.get_model()
    ]
    assert [t.access for t in sortedObjects] == [
        strip_markup(x[1]) for x in view.get_model()
    ]
    assert [t.file for t in sortedObjects] == [x[2] for x in view.get_model()]
    assert [t.mode for t in sortedObjects] == [
        strip_markup(x[6]) for x in view.get_model()
    ]


def test_status_markup(widget):
    def eq_status(*parts):
        return view.get_model()[0][0] == str.join(" / ", parts)

    view = widget.get_object("treeView")
    st_red = f'<span color="{Colors.RED}"><b>ST</b></span>'
    at_red = f'<span color="{Colors.RED}"><b>AT</b></span>'
    u_green = f'<span color="{Colors.GREEN}"><u><b>U</b></u></span>'
    st_green = f'<span color="{Colors.GREEN}"><u><b>ST</b></u></span>'
    at_green = f'<span color="{Colors.GREEN}"><u><b>AT</b></u></span>'

    # System trust
    widget.load_store([_mock_object(trust="ST", trust_status="U")], ids=[0])
    assert eq_status(st_red, "AT", "U")
    # System trust
    widget.load_store([_mock_object(trust="ST", trust_status="T")], ids=[0])
    assert eq_status(st_green, "AT", "U")
    # Ancillary trust, untrusted
    widget.load_store([_mock_object(trust="AT", trust_status="U")], ids=[0])
    assert eq_status("ST", at_red, "U")
    # Ancillary trust, trusted
    widget.load_store([_mock_object(trust="AT", trust_status="T")], ids=[0])
    assert eq_status("ST", at_green, "U")
    # Untrusted
    widget.load_store([_mock_object(trust="U", trust_status="U")], ids=[0])
    assert eq_status("ST", "AT", u_green)
    # Bad data
    widget.load_store([_mock_object(trust="foo")], ids=[0])
    assert eq_status("ST", "AT", "U")
    # Empty data
    widget.load_store([_mock_object()], ids=[0])
    assert eq_status("ST", "AT", "U")
    # Lowercase
    widget.load_store([_mock_object(trust="st", trust_status="u")], ids=[0])
    assert eq_status(st_red, "AT", "U")
    # Lowercase
    widget.load_store([_mock_object(trust="st", trust_status="t")], ids=[0])
    assert eq_status(st_green, "AT", "U")
    # Lowercase
    widget.load_store([_mock_object(trust="at", trust_status="u")], ids=[0])
    assert eq_status("ST", at_red, "U")
    # Lowercase
    widget.load_store([_mock_object(trust="at", trust_status="t")], ids=[0])
    assert eq_status("ST", at_green, "U")


def test_mode_markup(widget):
    view = widget.get_object("treeView")
    # Read
    widget.load_store([_mock_object(mode="R")], ids=[0])
    assert view.get_model()[0][6] == "<u><b>R</b></u>WX"
    # Write
    widget.load_store([_mock_object(mode="W")], ids=[0])
    assert view.get_model()[0][6] == "R<u><b>W</b></u>X"
    # Execute
    widget.load_store([_mock_object(mode="X")], ids=[0])
    assert view.get_model()[0][6] == "RW<u><b>X</b></u>"
    # Read/Write
    widget.load_store([_mock_object(mode="RW")], ids=[0])
    assert view.get_model()[0][6] == "<u><b>R</b></u><u><b>W</b></u>X"
    # Read/Execute
    widget.load_store([_mock_object(mode="RX")], ids=[0])
    assert view.get_model()[0][6] == "<u><b>R</b></u>W<u><b>X</b></u>"
    # Write/Execute
    widget.load_store([_mock_object(mode="WX")], ids=[0])
    assert view.get_model()[0][6] == "R<u><b>W</b></u><u><b>X</b></u>"
    # Full Access
    widget.load_store([_mock_object(mode="RWX")], ids=[0])
    assert view.get_model()[0][6] == "<u><b>R</b></u><u><b>W</b></u><u><b>X</b></u>"
    # Bad data
    widget.load_store([_mock_object(mode="foo")], ids=[0])
    assert view.get_model()[0][6] == "RWX"
    # Empty data
    widget.load_store([_mock_object()], ids=[0])
    assert view.get_model()[0][6] == "RWX"
    # Lowercase
    widget.load_store([_mock_object(mode="r")], ids=[0])
    assert view.get_model()[0][6] == "<u><b>R</b></u>WX"


def test_access_markup(widget):
    def eq_access(*parts):
        return view.get_model()[0][1] == str.join(" / ", parts)

    a_access = "<u><b>A</b></u>"
    d_access = "<u><b>D</b></u>"
    view = widget.get_object("treeView")

    # Allowed
    widget.load_store([_mock_object(access="A")], ids=[0])
    assert eq_access(a_access, "D")
    # Denied
    widget.load_store([_mock_object(access="D")], ids=[0])
    assert eq_access("A", d_access)
    # Bad data
    widget.load_store([_mock_object(access="foo")], ids=[0])
    assert eq_access("A", "D")
    # Empty data
    widget.load_store([_mock_object()], ids=[0])
    assert eq_access("A", "D")
    # Lowercase
    widget.load_store([_mock_object(access="a")], ids=[0])
    assert eq_access(a_access, "D")


def test_path_color(widget):
    view = widget.get_object("treeView")

    # Denied
    widget.load_store([_mock_object(access="D", mode="RWX")], ids=[0])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Full Access
    widget.load_store([_mock_object(access="A", mode="RWX")], ids=[0])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN
    assert view.get_model()[0][5] == Colors.BLACK
    # Partical Access
    widget.load_store([_mock_object(access="A", mode="R")], ids=[0])
    assert view.get_model()[0][4] == Colors.ORANGE
    assert view.get_model()[0][5] == Colors.BLACK
    # Bad data
    widget.load_store([_mock_object(access="foo")], ids=[0])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Empty data
    widget.load_store([_mock_object()], ids=[0])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Lowercase
    widget.load_store([_mock_object(access="a", mode="rwx")], ids=[0])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN
    assert view.get_model()[0][5] == Colors.BLACK


def test_update_tree_count(widget):
    widget.load_store([_mock_object()], ids=[0])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"1 {FILE_LABEL}"

    widget.load_store([_mock_object(), _mock_object()], ids=[0, 1])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"2 {FILES_LABEL}"


def test_fires_file_selection_changed_event(widget):
    mockHandler = MagicMock()
    widget.file_selection_changed += mockHandler
    mockData = _mock_object(file="foo")
    widget.load_store([mockData], ids=[0])
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with([mockData])


def test_shows_rule_view_from_context_menu(widget, mocker):
    mockHandler = MagicMock()
    widget.rule_view_activate += mockHandler
    widget.load_store(_objects, ids=_ids)
    view = widget.get_object("treeView")
    # select first item is list
    view.get_selection().select_path(Gtk.TreePath.new_first())
    # mock the reconile conext menu item click
    widget.reconcileContextMenu.get_children()[-1].activate()
    mockHandler.assert_called_with(rule_id=_ids[-1])
