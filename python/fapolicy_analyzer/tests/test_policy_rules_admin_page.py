import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from helpers import refresh_gui
from ui.policy_rules_admin_page import PolicyRulesAdminPage


def mock_users():
    mockUser = MagicMock(id=1)
    mockUser.name = "fooUser"
    return [mockUser]


def mock_groups():
    mockGroup = MagicMock(id=100)
    mockGroup.name = "fooGroup"
    return [mockGroup]


mock_events = [
    MagicMock(
        uid=1,
        gid=100,
        subject=MagicMock(file="fooSubject", trust="ST", access="A"),
        object=MagicMock(file="fooObject", trust="ST", access="A", mode="R"),
    )
]


@pytest.fixture
def widget(mocker):
    mock_system = MagicMock(
        users=MagicMock(return_value=mock_users()),
        groups=MagicMock(return_value=mock_groups()),
        events_from=MagicMock(return_value=mock_events),
    )
    mocker.patch("ui.policy_rules_admin_page.System", return_value=mock_system)
    widget = PolicyRulesAdminPage("foo")
    refresh_gui()
    return widget


@pytest.fixture
def userListView(widget):
    return widget.userList.get_object("treeView")


@pytest.fixture
def groupListView(widget):
    return widget.groupList.get_object("treeView")


@pytest.fixture
def subjectListView(widget):
    return widget.subjectList.get_object("treeView")


@pytest.fixture
def objectListView(widget):
    return widget.objectList.get_object("treeView")


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


def test_loads_users(widget, userListView):
    model = userListView.get_model()
    assert [x.name for x in mock_users()] == [x[0] for x in model]
    assert [x.id for x in mock_users()] == [x[1] for x in model]


def test_loads_groups(widget, groupListView):
    model = groupListView.get_model()
    assert [x.name for x in mock_groups()] == [x[0] for x in model]
    assert [x.id for x in mock_groups()] == [x[1] for x in model]


@pytest.mark.parametrize(
    "view, mockFnName",
    [
        (pytest.lazy_fixture("userListView"), "getUserDetails"),
        (pytest.lazy_fixture("groupListView"), "getGroupDetails"),
    ],
)
def test_updates_acl_details(widget, view, mockFnName, mocker):
    mocker.patch(f"ui.policy_rules_admin_page.acl.{mockFnName}", return_value="foo")
    textBuffer = widget.get_object("userDetails").get_buffer()
    view.get_selection().select_path(Gtk.TreePath.new_first())
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_subjects(widget, view, subjectListView):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    model = subjectListView.get_model()
    expectedSubject = mock_events[0].subject
    assert expectedSubject.trust in next(iter([x[0] for x in model]))
    assert expectedSubject.access in next(iter([x[1] for x in model]))
    assert expectedSubject.file == next(iter([x[2] for x in model]))


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_objects(widget, view, subjectListView, objectListView):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    model = objectListView.get_model()
    expectedObject = mock_events[0].object
    assert expectedObject.trust in next(iter([x[0] for x in model]))
    assert expectedObject.mode in next(iter([x[1] for x in model]))
    assert expectedObject.access in next(iter([x[2] for x in model]))
    assert expectedObject.file == next(iter([x[3] for x in model]))


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


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_handles_empty_acl_select(widget, view, subjectListView):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    assert widget.subjectList.get_ref().get_sensitive()
    assert len([x for x in subjectListView.get_model()]) > 0
    view.get_selection().unselect_all()
    textBuffer = widget.get_object("userDetails").get_buffer()
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == ""
    )
    assert not widget.subjectList.get_ref().get_sensitive()
    assert len([x for x in subjectListView.get_model()]) == 0


def test_handles_empty_subject_select(
    widget, userListView, subjectListView, objectListView
):
    userListView.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    textBuffer = widget.get_object("subjectDetails").get_buffer()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        != 0
    )
    assert widget.objectList.get_ref().get_sensitive()
    assert len([x for x in objectListView.get_model()]) > 0

    subjectListView.get_selection().unselect_all()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        == 0
    )
    assert not widget.objectList.get_ref().get_sensitive()
    assert len([x for x in objectListView.get_model()]) == 0


def test_handles_empty_object_select(
    widget, userListView, subjectListView, objectListView
):
    userListView.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    objectListView.get_selection().select_path(Gtk.TreePath.new_first())
    textBuffer = widget.get_object("objectDetails").get_buffer()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        != 0
    )

    subjectListView.get_selection().unselect_all()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        == 0
    )
