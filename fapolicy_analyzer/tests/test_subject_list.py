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

import context  # noqa: F401 # isort: skip
import re
from unittest.mock import MagicMock

import gi
import pytest
from callee.attributes import Attrs
from callee.collections import Sequence
from callee.types import InstanceOf
from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import APPLY_CHANGESETS
from fapolicy_analyzer.ui.changeset_wrapper import TrustChangeset
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.strings import FILE_LABEL, FILES_LABEL
from fapolicy_analyzer.ui.subject_list import _TRUST_RESP, _UNTRUST_RESP, SubjectList

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # isort: skip


def _mock_subject(trust="", access="", file="", trust_status=""):
    return MagicMock(trust=trust, access=access, file=file, trust_status=trust_status)


_systemTrust = [MagicMock(path="/st/foo")]
_ancillaryTrust = [MagicMock(path="/at/foo")]

_subjects = [
    _mock_subject(trust="ST", access="A", file="/tmp/foo", trust_status="T"),
    _mock_subject(trust="AT", access="D", file="/tmp/baz", trust_status="U"),
    _mock_subject(trust="U", access="P", file="/tmp/bar", trust_status="U"),
]


@pytest.fixture
def widget():
    return SubjectList()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_store(widget):
    def strip_markup(markup):
        return re.search(r"<b>([A-Z]*)</b>", markup).group(1)

    widget.load_store(_subjects)
    view = widget.get_object("treeView")
    sortedSubjects = sorted(_subjects, key=lambda s: s.file)
    assert [t.trust for t in sortedSubjects] == [
        strip_markup(x[0]) for x in view.get_model()
    ]
    assert [t.access for t in sortedSubjects] == [
        strip_markup(x[1]) for x in view.get_model()
    ]
    assert [t.file for t in sortedSubjects] == [x[2] for x in view.get_model()]


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
    widget.load_store([_mock_subject(trust="ST", trust_status="U")])
    assert eq_status(st_red, "AT", "U")
    # System trust
    widget.load_store([_mock_subject(trust="ST", trust_status="T")])
    assert eq_status(st_green, "AT", "U")
    # Ancillary trust, untrusted
    widget.load_store([_mock_subject(trust="AT", trust_status="U")])
    assert eq_status("ST", at_red, "U")
    # Ancillary trust, trusted
    widget.load_store([_mock_subject(trust="AT", trust_status="T")])
    assert eq_status("ST", at_green, "U")
    # Untrusted
    widget.load_store([_mock_subject(trust="U", trust_status="U")])
    assert eq_status("ST", "AT", u_green)
    # Bad data
    widget.load_store([_mock_subject(trust="foo")])
    assert eq_status("ST", "AT", "U")
    # Empty data
    widget.load_store([_mock_subject()])
    assert eq_status("ST", "AT", "U")
    # Lowercase
    widget.load_store([_mock_subject(trust="st", trust_status="u")])
    assert eq_status(st_red, "AT", "U")
    # Lowercase
    widget.load_store([_mock_subject(trust="st", trust_status="t")])
    assert eq_status(st_green, "AT", "U")
    # Lowercase
    widget.load_store([_mock_subject(trust="at", trust_status="u")])
    assert eq_status("ST", at_red, "U")
    # Lowercase
    widget.load_store([_mock_subject(trust="at", trust_status="t")])
    assert eq_status("ST", at_green, "U")


def test_access_markup(widget):
    def eq_access(*parts):
        return view.get_model()[0][1] == str.join(" / ", parts)

    a_access = "<u><b>A</b></u>"
    p_access = "<u><b>P</b></u>"
    d_access = "<u><b>D</b></u>"
    view = widget.get_object("treeView")

    # Allowed
    widget.load_store([_mock_subject(access="A")])
    assert eq_access(a_access, "P", "D")
    # Partial
    widget.load_store([_mock_subject(access="P")])
    assert eq_access("A", p_access, "D")
    # Denied
    widget.load_store([_mock_subject(access="D")])
    assert eq_access("A", "P", d_access)
    # Bad data
    widget.load_store([_mock_subject(access="foo")])
    assert eq_access("A", "P", "D")
    # Empty data
    widget.load_store([_mock_subject()])
    assert eq_access("A", "P", "D")
    # Lowercase
    widget.load_store([_mock_subject(access="a")])
    assert eq_access(a_access, "P", "D")


def test_path_color(widget):
    view = widget.get_object("treeView")

    # Allowed
    widget.load_store([_mock_subject(access="A")])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN
    assert view.get_model()[0][5] == Colors.BLACK
    # Partial
    widget.load_store([_mock_subject(access="P")])
    assert view.get_model()[0][4] == Colors.ORANGE
    assert view.get_model()[0][5] == Colors.BLACK
    # Denied
    widget.load_store([_mock_subject(access="D")])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Bad data
    widget.load_store([_mock_subject(access="foo")])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Empty data
    widget.load_store([_mock_subject()])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    assert view.get_model()[0][5] == Colors.WHITE
    # Lowercase
    widget.load_store([_mock_subject(access="a")])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN
    assert view.get_model()[0][5] == Colors.BLACK


def test_update_tree_count(widget):
    widget.load_store([_mock_subject()])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"1 {FILE_LABEL}"

    widget.load_store([_mock_subject(), _mock_subject()])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"2 {FILES_LABEL}"


def test_fires_file_selection_changed_event(widget):
    mockHandler = MagicMock()
    widget.file_selection_changed += mockHandler
    mockData = _mock_subject(file="foo")
    widget.load_store([mockData])
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with([mockData])


@pytest.mark.parametrize(
    "subject, databaseTrust",
    [
        (_mock_subject(trust="st", access="a", file="/st/foo"), _systemTrust[0]),
        (_mock_subject(trust="at", access="a", file="/at/foo"), _ancillaryTrust[0]),
        (_mock_subject(trust="u", access="a", file="/u/foo"), None),
    ],
)
def test_shows_reconciliation_dialog_on_double_click(
    subject, databaseTrust, widget, mocker
):
    mockDialog = mocker.patch(
        "fapolicy_analyzer.ui.subject_list.TrustReconciliationDialog",
        return_value=MagicMock(get_ref=MagicMock(spec=Gtk.Widget)),
    )
    widget.load_store(
        [subject], systemTrust=_systemTrust, ancillaryTrust=_ancillaryTrust
    )
    view = widget.get_object("treeView")
    view.row_activated(Gtk.TreePath.new_first(), view.get_column(0))
    mockDialog.assert_called_once_with(
        subject,
        databaseTrust=databaseTrust,
        parent=widget.get_ref().get_toplevel(),
    )


@pytest.mark.parametrize("response", [_UNTRUST_RESP, _TRUST_RESP])
def test_dispatches_changeset(response, widget, mocker):
    mockSubject = _mock_subject(trust="st", access="a", file="/foo")
    mockDialog = MagicMock(
        get_ref=MagicMock(return_value=MagicMock(run=MagicMock(return_value=response)))
    )
    mockChangeset = MagicMock(delete=MagicMock(), add=MagicMock(), spec=TrustChangeset)
    mocker.patch(
        "fapolicy_analyzer.ui.subject_list.TrustReconciliationDialog",
        return_value=mockDialog,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.subject_list.TrustChangeset", return_value=mockChangeset
    )
    mockDispatch = mocker.patch("fapolicy_analyzer.ui.subject_list.dispatch")

    widget.load_store([mockSubject])
    view = widget.get_object("treeView")
    view.row_activated(Gtk.TreePath.new_first(), view.get_column(0))
    mockDispatch.assert_called_once_with(
        InstanceOf(Action)
        & Attrs(
            type=APPLY_CHANGESETS,
            payload=Sequence(
                of=InstanceOf(TrustChangeset),
            ),
        )
    )

    if response == _UNTRUST_RESP:
        mockChangeset.delete.assert_called_once_with("/foo")
    elif response == _TRUST_RESP:
        mockChangeset.add.assert_called_once_with("/foo")


@pytest.mark.parametrize(
    "subject, databaseTrust",
    [
        (_mock_subject(trust="st", access="a", file="/st/foo"), _systemTrust[0]),
        (_mock_subject(trust="at", access="a", file="/at/foo"), _ancillaryTrust[0]),
        (_mock_subject(trust="u", access="a", file="/u/foo"), None),
    ],
)
def test_shows_reconciliation_dialog_from_context_menu(
    subject, databaseTrust, widget, mocker
):
    mockDialog = mocker.patch(
        "fapolicy_analyzer.ui.subject_list.TrustReconciliationDialog",
        return_value=MagicMock(get_ref=MagicMock(spec=Gtk.Widget)),
    )
    widget.load_store(
        [subject], systemTrust=_systemTrust, ancillaryTrust=_ancillaryTrust
    )
    view = widget.get_object("treeView")
    # select first item is list
    view.get_selection().select_path(Gtk.TreePath.new_first())
    # mock the reconcile context menu item click
    next(iter(widget.reconcileContextMenu.get_children())).activate()

    mockDialog.assert_called_once_with(
        subject,
        databaseTrust=databaseTrust,
        parent=widget.get_ref().get_toplevel(),
    )


@pytest.mark.parametrize(
    "subject",
    [
        _mock_subject(trust="st", access="a", file="/st/foo"),
        _mock_subject(trust="at", access="a", file="/at/foo"),
        _mock_subject(trust="u", access="a", file="/u/foo"),
    ],
)
def test_shows_change_trust_dialog_from_context_menu(subject, widget, mocker):
    mockDialog = mocker.patch(
        "fapolicy_analyzer.ui.subject_list.ConfirmChangeDialog",
        return_value=MagicMock(get_ref=MagicMock(spec=Gtk.Widget)),
    )
    widget.load_store(
        [subject], systemTrust=_systemTrust, ancillaryTrust=_ancillaryTrust
    )
    view = widget.get_object("treeView")
    view.get_selection().select_all()
    menu_item = next(iter(widget.fileChangeContextMenu.get_children()))
    menu_item.selection_data = (1, TrustChangeset())
    menu_item.activate()
    mockDialog.assert_called_once_with(
        parent=widget.get_ref().get_toplevel(), total=1, additions=0, deletions=0
    )


@pytest.mark.parametrize(
    "subjects",
    [
        [
            _mock_subject(trust="st", access="a", file="/st/foo"),
            _mock_subject(trust="st", access="a", file="/st/bar"),
        ],
        [
            _mock_subject(trust="at", access="a", file="/at/foo"),
            _mock_subject(trust="at", access="a", file="/at/bar"),
        ],
        [
            _mock_subject(trust="u", access="a", file="/u/foo"),
            _mock_subject(trust="u", access="a", file="/u/bar"),
        ],
    ],
)
def test_right_click_menu_and_select(subjects, widget):
    widget.load_store(
        subjects, systemTrust=_systemTrust, ancillaryTrust=_ancillaryTrust
    )
    widget.get_object("treeView")
    widget.get_object("treeSelection").select_all()
    event = Gdk.EventButton
    event.type = Gdk.EventType.BUTTON_PRESS
    event.button = 3
    event.x = 15
    event.y = 30
    widget.on_view_button_press_event(widget, event)


def test_get_selected_row_by_file(widget):
    widget.load_store(_subjects)
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    actual = widget.get_selected_row_by_file("/tmp/foo")
    _, paths = view.get_selection().get_selected_rows()
    expected = paths[0]
    assert expected.compare(actual)
