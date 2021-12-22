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


def _mock_object(trust="", mode="", access="", file=""):
    return MagicMock(trust=trust, mode=mode, access=access, file=file)


_objects = [
    _mock_object(trust="ST", mode="R", access="A", file="/tmp/foo"),
    _mock_object(trust="AT", mode="W", access="A", file="/tmp/baz"),
    _mock_object(trust="U", mode="X", access="D", file="/tmp/bar"),
]


@pytest.fixture
def widget():
    return ObjectList()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_store(widget):
    def strip_markup(markup):
        return re.search(r"<u>([A-Z]*)</u>", markup).group(1)

    widget.load_store(_objects)
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
        strip_markup(x[5]) for x in view.get_model()
    ]


def test_status_markup(widget):
    view = widget.get_object("treeView")

    # System trust
    widget.load_store([_mock_object(trust="ST")])
    assert view.get_model()[0][0] == "<b><u>ST</u></b>/AT/U"
    # Ancillary trust
    widget.load_store([_mock_object(trust="AT")])
    assert view.get_model()[0][0] == "ST/<b><u>AT</u></b>/U"
    # Untrusted
    widget.load_store([_mock_object(trust="U")])
    assert view.get_model()[0][0] == "ST/AT/<b><u>U</u></b>"
    # Bad data
    widget.load_store([_mock_object(trust="foo")])
    assert view.get_model()[0][0] == "ST/AT/U"
    # Empty data
    widget.load_store([_mock_object()])
    assert view.get_model()[0][0] == "ST/AT/U"
    # Lowercase
    widget.load_store([_mock_object(trust="st")])
    assert view.get_model()[0][0] == "<b><u>ST</u></b>/AT/U"


def test_mode_markup(widget):
    view = widget.get_object("treeView")

    # Read
    widget.load_store([_mock_object(mode="R")])
    assert view.get_model()[0][5] == "<b><u>R</u></b>WX"
    # Write
    widget.load_store([_mock_object(mode="W")])
    assert view.get_model()[0][5] == "R<b><u>W</u></b>X"
    # Execute
    widget.load_store([_mock_object(mode="X")])
    assert view.get_model()[0][5] == "RW<b><u>X</u></b>"
    # Read/Write
    widget.load_store([_mock_object(mode="RW")])
    assert view.get_model()[0][5] == "<b><u>R</u></b><b><u>W</u></b>X"
    # Read/Execute
    widget.load_store([_mock_object(mode="RX")])
    assert view.get_model()[0][5] == "<b><u>R</u></b>W<b><u>X</u></b>"
    # Write/Execute
    widget.load_store([_mock_object(mode="WX")])
    assert view.get_model()[0][5] == "R<b><u>W</u></b><b><u>X</u></b>"
    # Full Access
    widget.load_store([_mock_object(mode="RWX")])
    assert view.get_model()[0][5] == "<b><u>R</u></b><b><u>W</u></b><b><u>X</u></b>"
    # Bad data
    widget.load_store([_mock_object(mode="foo")])
    assert view.get_model()[0][5] == "RWX"
    # Empty data
    widget.load_store([_mock_object()])
    assert view.get_model()[0][5] == "RWX"
    # Lowercase
    widget.load_store([_mock_object(mode="r")])
    assert view.get_model()[0][5] == "<b><u>R</u></b>WX"


def test_access_markup(widget):
    view = widget.get_object("treeView")

    # Allowed
    widget.load_store([_mock_object(access="A")])
    assert view.get_model()[0][1] == "<b><u>A</u></b>/D"
    # Denied
    widget.load_store([_mock_object(access="D")])
    assert view.get_model()[0][1] == "A/<b><u>D</u></b>"
    # Bad data
    widget.load_store([_mock_object(access="foo")])
    assert view.get_model()[0][1] == "A/D"
    # Empty data
    widget.load_store([_mock_object()])
    assert view.get_model()[0][1] == "A/D"
    # Lowercase
    widget.load_store([_mock_object(access="a")])
    assert view.get_model()[0][1] == "<b><u>A</u></b>/D"


def test_path_color(widget):
    view = widget.get_object("treeView")

    # Denied
    widget.load_store([_mock_object(access="D", mode="RWX")])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    # Full Access
    widget.load_store([_mock_object(access="A", mode="RWX")])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN
    # Partical Access
    widget.load_store([_mock_object(access="A", mode="R")])
    assert view.get_model()[0][4] == Colors.ORANGE
    # Bad data
    widget.load_store([_mock_object(access="foo")])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    # Empty data
    widget.load_store([_mock_object()])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    # Lowercase
    widget.load_store([_mock_object(access="a", mode="rwx")])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN


def test_update_tree_count(widget):
    widget.load_store([_mock_object()])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"1 {FILE_LABEL}"

    widget.load_store([_mock_object(), _mock_object()])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"2 {FILES_LABEL}"


def test_fires_file_selection_changed_event(widget):
    mockHandler = MagicMock()
    widget.file_selection_changed += mockHandler
    mockData = _mock_object(file="foo")
    widget.load_store([mockData])
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with([mockData])
