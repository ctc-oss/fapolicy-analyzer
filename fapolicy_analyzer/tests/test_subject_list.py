import context  # noqa: F401
import gi
import pytest
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.configs import Colors
from ui.subject_list import SubjectList
from ui.strings import FILE_LABEL, FILES_LABEL


def _mock_subject(trust="", access="", file=""):
    return MagicMock(trust=trust, access=access, file=file)


_subjects = [
    _mock_subject(trust="ST", access="A", file="/tmp/foo"),
    _mock_subject(trust="AT", access="D", file="/tmp/baz"),
    _mock_subject(trust="U", access="P", file="/tmp/bar"),
]


@pytest.fixture
def widget():
    return SubjectList()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_store(widget):
    def strip_markup(markup):
        return re.search(r"<u>([A-Z]*)</u>", markup).group(1)

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
    view = widget.get_object("treeView")

    # System trust
    widget.load_store([_mock_subject(trust="ST")])
    assert view.get_model()[0][0] == "<b><u>ST</u></b>/AT/U"
    # Ancillary trust
    widget.load_store([_mock_subject(trust="AT")])
    assert view.get_model()[0][0] == "ST/<b><u>AT</u></b>/U"
    # Untrusted
    widget.load_store([_mock_subject(trust="U")])
    assert view.get_model()[0][0] == "ST/AT/<b><u>U</u></b>"
    # Bad data
    widget.load_store([_mock_subject(trust="foo")])
    assert view.get_model()[0][0] == "ST/AT/U"
    # Empty data
    widget.load_store([_mock_subject()])
    assert view.get_model()[0][0] == "ST/AT/U"
    # Lowercase
    widget.load_store([_mock_subject(trust="st")])
    assert view.get_model()[0][0] == "<b><u>ST</u></b>/AT/U"


def test_access_markup(widget):
    view = widget.get_object("treeView")

    # Allowed
    widget.load_store([_mock_subject(access="A")])
    assert view.get_model()[0][1] == "<b><u>A</u></b>/P/D"
    # Partial
    widget.load_store([_mock_subject(access="P")])
    assert view.get_model()[0][1] == "A/<b><u>P</u></b>/D"
    # Denied
    widget.load_store([_mock_subject(access="D")])
    assert view.get_model()[0][1] == "A/P/<b><u>D</u></b>"
    # Bad data
    widget.load_store([_mock_subject(access="foo")])
    assert view.get_model()[0][1] == "A/P/D"
    # Empty data
    widget.load_store([_mock_subject()])
    assert view.get_model()[0][1] == "A/P/D"
    # Lowercase
    widget.load_store([_mock_subject(access="a")])
    assert view.get_model()[0][1] == "<b><u>A</u></b>/P/D"


def test_path_color(widget):
    view = widget.get_object("treeView")

    # Allowed
    widget.load_store([_mock_subject(access="A")])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN
    # Partial
    widget.load_store([_mock_subject(access="P")])
    assert view.get_model()[0][4] == Colors.LIGHT_YELLOW
    # Denied
    widget.load_store([_mock_subject(access="D")])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    # Bad data
    widget.load_store([_mock_subject(access="foo")])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    # Empty data
    widget.load_store([_mock_subject()])
    assert view.get_model()[0][4] == Colors.LIGHT_RED
    # Lowercase
    widget.load_store([_mock_subject(access="a")])
    assert view.get_model()[0][4] == Colors.LIGHT_GREEN


def test_update_tree_count(widget):
    widget.load_store([_mock_subject()])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"1 {FILE_LABEL}"

    widget.load_store([_mock_subject(), _mock_subject()])
    label = widget.get_object("treeCount")
    assert label.get_text() == f"2 {FILES_LABEL}"


def test_fires_subject_selection_changed_event(widget):
    mockHandler = MagicMock()
    widget.subject_selection_changed += mockHandler
    mockData = _mock_subject(file="foo")
    widget.load_store([mockData])
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with(mockData)
