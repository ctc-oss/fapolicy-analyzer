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
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.object_list import ObjectList
from fapolicy_analyzer.ui.strings import FILE_LABEL, FILES_LABEL


def _mock_object(trust="", perm="", access="", file="", trust_status=""):
    return MagicMock(
        trust=trust, perm=perm, access=access, file=file, trust_status=trust_status
    )


_objects = [
    {
        0: _mock_object(
            trust="ST", perm="any / open / access", access="A", file="/tmp/foo", trust_status="U"
        )
    },
    {
        1: _mock_object(
            trust="AT", perm="any / open / access", access="A", file="/tmp/baz", trust_status="U"
        )
    },
    {
        2: _mock_object(
            trust="U", perm="any / open / access", access="D", file="/tmp/bar", trust_status="U"
        )
    },
]


@pytest.fixture
def widget():
    return ObjectList()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_store(widget):
    def strip_markup(markup):
        return re.search(r"<b>([A-Z]*)</b>", markup).group(1)

    widget.load_store(_objects)
    view = widget.get_object("treeView")
    sortedObjects = sorted(_objects, key=lambda o: next(iter(o.values())).file)
    assert [next(iter(t.values())).trust for t in sortedObjects] == [
        strip_markup(x[0]) for x in view.get_model()
    ]
    assert [next(iter(t.values())).access for t in sortedObjects] == [
        strip_markup(x[1]) for x in view.get_model()
    ]
    assert [next(iter(t.values())).file for t in sortedObjects] == [
        x[2] for x in view.get_model()
    ]
    assert [next(iter(t.values())).perm for t in sortedObjects] == [
        x[6] for x in view.get_model()
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
    widget.load_store([{0: _mock_object(trust="ST", trust_status="U")}])
    assert eq_status(st_red, "AT", "U")
    # System trust
    widget.load_store([{0: _mock_object(trust="ST", trust_status="T")}])
    assert eq_status(st_green, "AT", "U")
    # Ancillary trust, untrusted
    widget.load_store([{0: _mock_object(trust="AT", trust_status="U")}])
    assert eq_status("ST", at_red, "U")
    # Ancillary trust, trusted
    widget.load_store([{0: _mock_object(trust="AT", trust_status="T")}])
    assert eq_status("ST", at_green, "U")
    # Untrusted
    widget.load_store([{0: _mock_object(trust="U", trust_status="U")}])
    assert eq_status("ST", "AT", u_green)
    # Bad data
    widget.load_store([{0: _mock_object(trust="foo")}])
    assert eq_status("ST", "AT", "U")
    # Empty data
    widget.load_store([{0: _mock_object()}])
    assert eq_status("ST", "AT", "U")
    # Lowercase
    widget.load_store([{0: _mock_object(trust="st", trust_status="u")}])
    assert eq_status(st_red, "AT", "U")
    # Lowercase
    widget.load_store([{0: _mock_object(trust="st", trust_status="t")}])
    assert eq_status(st_green, "AT", "U")
    # Lowercase
    widget.load_store([{0: _mock_object(trust="at", trust_status="u")}])
    assert eq_status("ST", at_red, "U")
    # Lowercase
    widget.load_store([{0: _mock_object(trust="at", trust_status="t")}])
    assert eq_status("ST", at_green, "U")


def test_perm_markup(widget):
    view = widget.get_object("treeView")
    # Read
    widget.load_store([{0: _mock_object(perm="any / open / access")}])
    assert view.get_model()[0][6] == "any / open / access"


def test_access_markup(widget):
    def eq_access(*parts):
        return view.get_model()[0][1] == str.join(" / ", parts)

    a_access = "<u><b>A</b></u>"
    d_access = "<u><b>D</b></u>"
    view = widget.get_object("treeView")

    # Allowed
    widget.load_store([{0: _mock_object(access="A")}])
    assert eq_access(a_access, "D")
    # Denied
    widget.load_store([{0: _mock_object(access="D")}])
    assert eq_access("A", d_access)
    # Bad data
    widget.load_store([{0: _mock_object(access="foo")}])
    assert eq_access("A", "D")
    # Empty data
    widget.load_store([{0: _mock_object()}])
    assert eq_access("A", "D")
    # Lowercase
    widget.load_store([{0: _mock_object(access="a")}])
    assert eq_access(a_access, "D")


def test_path_color(widget):
    view = widget.get_object("treeView")

    # Denied
    widget.load_store([{0: _mock_object(access="D", perm="any / open / access")}])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Full Access
    widget.load_store([{0: _mock_object(access="A", perm="any / open / access")}])
    assert view.get_model()[0][4] == Colors.ORANGE
    assert view.get_model()[0][5] == Colors.BLACK
    # Partical Access
    widget.load_store([{0: _mock_object(access="A", perm="any / open / access")}])
    assert view.get_model()[0][4] == Colors.ORANGE
    assert view.get_model()[0][5] == Colors.BLACK
    # Bad data
    widget.load_store([{0: _mock_object(access="foo")}])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Empty data
    widget.load_store([{0: _mock_object()}])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Lowercase
    widget.load_store([{0: _mock_object(access="a", perm="any / open / access")}])
    assert view.get_model()[0][4] == Colors.ORANGE
    assert view.get_model()[0][5] == Colors.BLACK


def test_update_tree_count(widget):
    widget.load_store([{0: _mock_object()}])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"1 {FILE_LABEL}"

    widget.load_store([{0: _mock_object()}, {1: _mock_object()}])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"2 {FILES_LABEL}"


def test_fires_file_selection_changed_event(widget):
    mockHandler = MagicMock()
    widget.file_selection_changed += mockHandler
    mockData = _mock_object(file="foo")
    widget.load_store([{0: mockData}])
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with([mockData])


def test_shows_rule_view_from_context_menu(widget, mocker):
    mockHandler = MagicMock()
    widget.rule_view_activate += mockHandler
    widget.load_store(_objects)
    view = widget.get_object("treeView")
    # select first item is list
    view.get_selection().select_path(Gtk.TreePath.new_first())
    # mock the reconile conext menu item click
    widget.reconcileContextMenu.get_children()[-1].activate()
    mockHandler.assert_called_with(rule_id=next(iter(_objects[-1].keys())))
